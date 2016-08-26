---
title: Python多线程模块threading源码
date: 2016-08-20 13:42:05
tags:
- Python
- 多线程
- threading
categories:
- Python
---

threading模块包含了：
+ 线程对象Thread
+ 普通锁对象Lock
+ 可重入锁对象RLock
+ 条件锁对象Condition
+ 事件对象Event
+ 信号量对象Semaphore
+ 定时器对象Timer

<!-- more -->
## threading.Thread

## threading.Lock

锁对象Lock在threading模块中的定义只有两句，也就是说Lock其实就是thread中的allocate\_lock函数。

这个锁对象只有**locked**和**unlocked**两种状态，当处于**locked**状态时，它是没有拥有者这个概念的。也就是说线程A调用了acquire()函数获取了锁，并不一定说只能由A来调用release()函数释放该锁，可以由线程B调用release()函数来释放该锁。

还有一个特性就是这个锁对象是不可重入的，也就是说如果线程A调用了acquire()函数获取了该锁，如果线程A再次调用acquire()函数获取锁，那么线程A就会陷入死锁，除非有其它线程调用了release()函数释放该锁。**Condition**对象就是使用这两个特性实现的。

```python
_allocate_lock = thread.allocate_lock
Lock = _allocate_lock
```
## threading.RLock

RLock对象的内部是使用Lock对象来实现的，不过又增添了某些功能。
+ RLock对象是有拥有者这个概念的，即只能由获得了RLock对象的线程来调用release函数来释放锁。
+ RLock对象是可重入的，即一个线程可以多次获得RLock对象，RLock对象会在内部维护一个计数，统计该线程获得了自己多少次，释放该锁时，会在内部将计数减1，只有当计数为0时才真正地释放了该锁。

```python
def RLock(*args, **kwargs):
	'''
	可以看出，RLock其实是一个工厂函数，返回一个可重入锁对象。
	可重入锁是有拥有者这个概念的，哪个线程获取了该锁，那么哪个就是该锁的拥有者，
	只有拥有者才能够释放该锁，如果非拥有者释放该锁，那么就会引起一个错误。
	'''
    return _RLock(*args, **kwargs)

class _RLock(_Verbose):

    def __init__(self, verbose=None):
	'''
	可以看出RLock对象内部也是基于thread.allocate_lock的，
	self.__owner表示该锁的拥有者
	self.__count用来记录该锁被同一个线程获取了几次，
	锁的拥有者每调用一次release()就将self.__count减1，当其为0时才能够
	释放self.__block
	'''
        _Verbose.__init__(self, verbose)
        self.__block = _allocate_lock()
        self.__owner = None
        self.__count = 0

    def __repr__(self):
        owner = self.__owner
        try:
            owner = _active[owner].name
        except KeyError:
            pass
        return "<%s owner=%r count=%d>" % (
                self.__class__.__name__, owner, self.__count)

    def acquire(self, blocking=1):
	#_get_ident是获取线程id的函数
        me = _get_ident()
	#如果是锁的拥有者再次获取该锁，那么就将self.__count + 1
        if self.__owner == me:
            self.__count = self.__count + 1
            if __debug__:
                self._note("%s.acquire(%s): recursive success", self, blocking)
            return 1

	#如果不是该锁的拥有者，那么就让其获取锁
        rc = self.__block.acquire(blocking)

	#如果成功获取到了该锁，那么就修改self.__owner和self.__count
        if rc:
            self.__owner = me
            self.__count = 1
            if __debug__:
                self._note("%s.acquire(%s): initial success", self, blocking)
        else:
            if __debug__:
                self._note("%s.acquire(%s): failure", self, blocking)
        return rc

    __enter__ = acquire

    def release(self):
	#如果不是锁的拥有者释放该锁，那就会引起一个错误。
        if self.__owner != _get_ident():
            raise RuntimeError("cannot release un-acquired lock")
	#释放锁其实就是将锁的self.__count减1
        self.__count = count = self.__count - 1
	#当self.__count减为0时，才能够释放self.__block
        if not count:
            self.__owner = None
            self.__block.release()
            if __debug__:
                self._note("%s.release(): final release", self)
        else:
            if __debug__:
                self._note("%s.release(): non-final release", self)

    def __exit__(self, t, v, tb):
        self.release()

	
	#下面的这些内部方法是给Condition对象使用的
	#Condition对象的内部依赖于锁对象，可以是Lock对象，也可以是RLock对象。
	#如果是RLock对象的话，情况比较特殊。

    def _release_save(self):
	#当一个线程调用Condition对象的wait方法时，表示释放锁，然后进入休眠
	#那就需要保存现场，当线程苏醒并再次获取该锁时就需要恢复现场。
        if __debug__:
            self._note("%s._release_save()", self)
        count = self.__count
        self.__count = 0
        owner = self.__owner
        self.__owner = None
        self.__block.release()
        return (count, owner)

    def _acquire_restore(self, count_owner):
	#根据传进来的count_owner对象恢复现场
        count, owner = count_owner
        self.__block.acquire()
        self.__count = count
        self.__owner = owner
        if __debug__:
            self._note("%s._acquire_restore()", self)


    def _is_owned(self):
        return self.__owner == _get_ident()
```

## threading.Condition
考虑这么一个场景，多线程需要互斥访问一个队列，某些线程从队列中读取元素，并删除读取的元素；某些线程将元素加入到队列中。如果读取元素的线程获得了锁，当时发现需要的条件不满足，即队列为空，它无法获得元素。那么此时一个选择就是该线程释放锁，等待线下次获得锁时再查看队列中有没有元素。另一个选择就是使得该线程阻塞在该锁上，当其他写线程向队列中加入元素后，就唤醒阻塞在该锁上的线程。

使用条件锁就能使得当获得锁的某个线程发现所需要的条件不满足时，使自己阻塞在该锁上。
+ 条件锁的内部是使用Lock或者RLock实现的，我们可以通过参数指定其通过哪种锁实现。条件锁在此基础上增加了阻塞等待的功能。
+ 条件锁内部维护一个阻塞队列，当线程调用wait方法时，就将线程加入阻塞队列（具体不是这样，为了方便理解所以这样说）。当其它线程调用notify方法时就唤醒队列中的元素。notify方法默认唤醒队列的第一个元素，我们可以指定参数，使其唤醒前n个线程。

```python
def Condition(*args, **kwargs):
	'''
	可以看出这也是一个工厂方法。
	条件锁内部维护一个阻塞队列，当获取了锁的线程对象如果判断某些条件不满足导致无法往下执行，
	那么就会调用wait方法，当其他线程对象满足了这些条件，那么就会调用notify方法来唤醒队列中的线程。
	'''
    return _Condition(*args, **kwargs)

class _Condition(_Verbose):
	'''
	条件锁对象允许多个线程在其阻塞队列中等待，直到被其它线程唤醒
	'''

    def __init__(self, lock=None, verbose=None):
        _Verbose.__init__(self, verbose)
		#我们可以指定条件锁内部所使用的锁，如果没有指定，那么内部默认使用RLock，因为该锁更安全。
        if lock is None:
            lock = RLock()
        self.__lock = lock
		#导入锁的方法到自身
        self.acquire = lock.acquire
        self.release = lock.release

		#Condition内部已经实现了下面的方法
		#但是如果使用的是RLock对象，那么就需要覆盖这些方法
		#因为RLock对象在Condition对象被调用wait时需要保存现场
		#和恢复现场。
        try:
            self._release_save = lock._release_save
        except AttributeError:
            pass
        try:
            self._acquire_restore = lock._acquire_restore
        except AttributeError:
            pass
        try:
            self._is_owned = lock._is_owned
        except AttributeError:
            pass
		#阻塞队列
        self.__waiters = []

    def __enter__(self):
        return self.__lock.__enter__()

    def __exit__(self, *args):
        return self.__lock.__exit__(*args)

    def __repr__(self):
        return "<Condition(%s, %d)>" % (self.__lock, len(self.__waiters))

    def _release_save(self):
        self.__lock.release()           # No state to save

    def _acquire_restore(self, x):
        self.__lock.acquire()           # Ignore saved state

    def _is_owned(self):
        # Return True if lock is owned by current_thread.
        # This method is called only if __lock doesn't have _is_owned().
        if self.__lock.acquire(0):
            self.__lock.release()
            return False
        else:
            return True

    def wait(self, timeout=None):
	'''
	阻塞等待直到其它线程调用了notify函数，或者超时时间到了。
	只有获得了锁的线程才能够调用wait函数
	'''
        if not self._is_owned():
            raise RuntimeError("cannot wait on un-acquired lock")

	#让一个线程wait其实就是分配给该线程一个锁，然后让其连续两次调用锁的acquire()方法
        waiter = _allocate_lock()
	#第一次调用
        waiter.acquire()
	#阻塞队列中存的是锁对象，其实线程notify时其实就是release阻塞队列中的锁对象。
        self.__waiters.append(waiter)
        saved_state = self._release_save()
        try:    # restore state no matter what (e.g., KeyboardInterrupt)
            if timeout is None:
			#第二次调用，如果没有设置超时时间
                waiter.acquire()
                if __debug__:
                    self._note("%s.wait(): got it", self)
            else:
			#如果使用死循环来不断地获得锁，那么太耗费CPU资源了
			#所以每隔一段时间获得锁一次，如果获得锁，那么就跳出循环
			#否则就继续sleep，直到睡眠的总时间达到了timeout。
                endtime = _time() + timeout
                delay = 0.0005 # 500 us -> initial delay of 1 ms
                while True:
                    gotit = waiter.acquire(0)
                    if gotit:
                        break
                    remaining = endtime - _time()
                    if remaining <= 0:
                        break
                    delay = min(delay * 2, remaining, .05)
                    _sleep(delay)
                if not gotit:
                    if __debug__:
                        self._note("%s.wait(%s): timed out", self, timeout)
                    try:
                        self.__waiters.remove(waiter)
                    except ValueError:
                        pass
                else:
                    if __debug__:
                        self._note("%s.wait(%s): got it", self, timeout)
        finally:
            self._acquire_restore(saved_state)

    def notify(self, n=1):
	#只有锁的拥有者才能调用notify
        if not self._is_owned():
            raise RuntimeError("cannot notify on un-acquired lock")
        __waiters = self.__waiters
        waiters = __waiters[:n]
        if not waiters:
            if __debug__:
                self._note("%s.notify(): no waiters", self)
            return
        self._note("%s.notify(): notifying %d waiter%s", self, n,
                   n!=1 and "s" or "")
        for waiter in waiters:
		#释放锁，那么阻塞队列中的线程就会被解除死锁的状态，从而能够往下执行。
            waiter.release()
            try:
                __waiters.remove(waiter)
            except ValueError:
                pass

    def notifyAll(self):
	#唤醒等待队列中的所有线程
        self.notify(len(self.__waiters))

    notify_all = notifyAll
```
## threading.Event

Event对象是一个特殊的条件锁对象，其内部是基础Condition对象实现的。
+ Event是某些场景下的条件锁，比如多少线程等待某个事件发生，在事件发生后，所有的线程都会被激活。比如说主线程完成初始化功能后，就相当于某个事件发生了，那么所有的子线程都应当被激活，然后开始各自的工作。
+ 所以说这可以看做是线程间通信的一种方法，只不过这种通信方法能够传递的消息比较简单。
```python

def Event(*args, **kwargs):
	'''
	工厂方法
	'''
    return _Event(*args, **kwargs)

class _Event(_Verbose):

    def __init__(self, verbose=None):
        _Verbose.__init__(self, verbose)
        self.__cond = Condition(Lock())
        self.__flag = False

    def _reset_internal_locks(self):
        # private!  called by Thread._reset_internal_locks by _after_fork()
        self.__cond.__init__()

    def isSet(self):
        'Return true if and only if the internal flag is true.'
        return self.__flag

    is_set = isSet

    def set(self):
	'''
	设置内部的flag为true，
	并且唤醒所有阻塞在该事件上的所有线程
	'''
        self.__cond.acquire()
        try:
            self.__flag = True
            self.__cond.notify_all()
        finally:
            self.__cond.release()

    def clear(self):
	'''
	清除内部标记，只有Event对象又可以再次使用了。
	'''
        self.__cond.acquire()
        try:
            self.__flag = False
        finally:
            self.__cond.release()

    def wait(self, timeout=None):
	'''
	阻塞直到内部的flag为True，或者超时时间到达。
	'''
        self.__cond.acquire()
        try:
            if not self.__flag:
                self.__cond.wait(timeout)
            return self.__flag
        finally:
            self.__cond.release()
```
## threading.Semaphore

```python
def Semaphore(*args, **kwargs):
    """A factory function that returns a new semaphore.

    Semaphores manage a counter representing the number of release() calls minus
    the number of acquire() calls, plus an initial value. The acquire() method
    blocks if necessary until it can return without making the counter
    negative. If not given, value defaults to 1.

    """
    return _Semaphore(*args, **kwargs)

class _Semaphore(_Verbose):
    """Semaphores manage a counter representing the number of release() calls
       minus the number of acquire() calls, plus an initial value. The acquire()
       method blocks if necessary until it can return without making the counter
       negative. If not given, value defaults to 1.

    """

    # After Tim Peters' semaphore class, but not quite the same (no maximum)

    def __init__(self, value=1, verbose=None):
        if value < 0:
            raise ValueError("semaphore initial value must be >= 0")
        _Verbose.__init__(self, verbose)
        self.__cond = Condition(Lock())
        self.__value = value

    def acquire(self, blocking=1):
        """Acquire a semaphore, decrementing the internal counter by one.

        When invoked without arguments: if the internal counter is larger than
        zero on entry, decrement it by one and return immediately. If it is zero
        on entry, block, waiting until some other thread has called release() to
        make it larger than zero. This is done with proper interlocking so that
        if multiple acquire() calls are blocked, release() will wake exactly one
        of them up. The implementation may pick one at random, so the order in
        which blocked threads are awakened should not be relied on. There is no
        return value in this case.

        When invoked with blocking set to true, do the same thing as when called
        without arguments, and return true.

        When invoked with blocking set to false, do not block. If a call without
        an argument would block, return false immediately; otherwise, do the
        same thing as when called without arguments, and return true.

        """
        rc = False
        with self.__cond:
            while self.__value == 0:
                if not blocking:
                    break
                if __debug__:
                    self._note("%s.acquire(%s): blocked waiting, value=%s",
                            self, blocking, self.__value)
                self.__cond.wait()
            else:
                self.__value = self.__value - 1
                if __debug__:
                    self._note("%s.acquire: success, value=%s",
                            self, self.__value)
                rc = True
        return rc

    __enter__ = acquire

    def release(self):
        """Release a semaphore, incrementing the internal counter by one.

        When the counter is zero on entry and another thread is waiting for it
        to become larger than zero again, wake up that thread.

        """
        with self.__cond:
            self.__value = self.__value + 1
            if __debug__:
                self._note("%s.release: success, value=%s",
                        self, self.__value)
            self.__cond.notify()

    def __exit__(self, t, v, tb):
        self.release()

```


## threading.BoundedSemaphore
```python
def BoundedSemaphore(*args, **kwargs):
    """A factory function that returns a new bounded semaphore.

    A bounded semaphore checks to make sure its current value doesn't exceed its
    initial value. If it does, ValueError is raised. In most situations
    semaphores are used to guard resources with limited capacity.

    If the semaphore is released too many times it's a sign of a bug. If not
    given, value defaults to 1.

    Like regular semaphores, bounded semaphores manage a counter representing
    the number of release() calls minus the number of acquire() calls, plus an
    initial value. The acquire() method blocks if necessary until it can return
    without making the counter negative. If not given, value defaults to 1.

    """
    return _BoundedSemaphore(*args, **kwargs)

class _BoundedSemaphore(_Semaphore):
    """A bounded semaphore checks to make sure its current value doesn't exceed
       its initial value. If it does, ValueError is raised. In most situations
       semaphores are used to guard resources with limited capacity.
    """

    def __init__(self, value=1, verbose=None):
        _Semaphore.__init__(self, value, verbose)
        self._initial_value = value

    def release(self):
        """Release a semaphore, incrementing the internal counter by one.

        When the counter is zero on entry and another thread is waiting for it
        to become larger than zero again, wake up that thread.

        If the number of releases exceeds the number of acquires,
        raise a ValueError.

        """
        with self._Semaphore__cond:
            if self._Semaphore__value >= self._initial_value:
                raise ValueError("Semaphore released too many times")
            self._Semaphore__value += 1
            self._Semaphore__cond.notify()


```
## threading.Timer
定时器对象。
```python
def Timer(*args, **kwargs):
	'''
	工厂方法
	'''
    return _Timer(*args, **kwargs)

class _Timer(Thread):
    """Call a function after a specified number of seconds:

            t = Timer(30.0, f, args=[], kwargs={})
            t.start()
            t.cancel()     # stop the timer's action if it's still waiting

    """

    def __init__(self, interval, function, args=[], kwargs={}):
        Thread.__init__(self)
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.finished = Event()

    def cancel(self):
	#取消计时器，其实就是让计时器超时时不调用传进来的function函数
        self.finished.set()

    def run(self):
	#其实就是让Event对象在selfinterval后超时
        self.finished.wait(self.interval)
	#如果超时之后，且没有调用过cancel方法，那么就调用传进来的function函数
        if not self.finished.is_set():
            self.function(*self.args, **self.kwargs)
        self.finished.set()
```
参考：
[Python多线程（threading）学习总结](http://blog.csdn.net/zhanh1218/article/details/32131385)
