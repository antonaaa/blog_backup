---
title: Python属性和方法 
date: 2016-08-18 17:56:55
tags:
- Python
categories:
- Python
---

关于这本书
解释了访问Python新式类对象属性的过程
+ 函数(functions)如何变成方法(methods)
+ 描述符(descriptors)和属性(properties)是如何工作的。
+ 定义方法解析的顺序


## 开始之前
一些你应该知道的事情：
+ 这本书的内容覆盖了新式类。书中的例子对Python2.5和Python3.x是有效的。
+ 这本书不是写给Python初学者的，是写给那些知道Python，但是想知道更多的。
+ 你应该知道Python中不同对象的类型，当你使用type方法时，你应该知道能得到什么样的结果。你应该阅读这系列书的第一个部分[Python Types and Objects]。

## 属性的访问

### 动态字典\_\_dict\_\_

```python
>>> class C(object):
...     classattr = "attr on class"  1
...
>>> cobj = C()
>>> cobj.instattr = "attr on instance"  2
>>>
>>> cobj.instattr  3
'attr on instance'
>>> cobj.classattr 4
'attr on class'
>>> C.__dict__['classattr'] 5
'attr on class'
>>> cobj.__dict__['instattr'] 6
'attr on instance'
>>>
>>> cobj.__dict__ 7
{'instattr': 'attr on instance'}
>>> C.__dict__ 8
{'classattr': 'attr on class', '__module__': '__main__', '__doc__': None}
```

* 1 类能够设置自己的属性。
* 2 类的实例能够设置自己的属性。
* 34 类和实例的属性都能够通过实例访问。
* 56 属性最终是存在在对象的字典\_\_dict\_\_中。
* 78 \_\_dict\_\_只存储用户定义的属性(user-provided attributes)。 

像\_\_dict\_\_，\_\_bases\_\_，\_\_class\_\_这些属性都是Python提供(Python-proviede)的。
通常情况下，用户定义的属性（user-defined attributes)是存储在该对象的\_\_dict\_\_中，但不总是这样，因为一些内置的对象是没有\_\_dict\_\_属性的（如list，tuple等）。

当我们访问一个属性(objname.attributename)时，Python解释器会按顺序在以下的对象中查看该属性。
1. 在对象本身中查看该属性（在objname.\_\_dict\_\_中或者Python提供的属性中查找）。
2. 在对象的类中查找（objname.\_\_class\_\_.\_\_dict\_\_)。注意了，只会在该对象的类的\_\_dict\_\_中查找，也即以为着只会在类中查找用户提供的属性，而不会查看Python提供的属性。比如说当访问objname.\_\_bases\_\_时会引起错误。
3. 会在该类的基类，以及基类的基类的\_\_dict\_\_中查看该属性。直到该属性被找到或者搜索完所有的基类，基类搜索的顺序在新式类中是使用广度优先的查找算法，而在旧式类中是使用深度优先的查找算法。

如果查找了以上所有的对象都没有查找到该属性，那么就会抛出一个异常**AttributeError**。当通过对象访问一个属性时，类型的类型是永远不会被查找的（objname.\_\_class\_\_.\_\_class\_\_)。

以上的部分解释了通常情况下通过对象访问属性的原理，通过类(classname.attributename)访问属性的原理也是类似的，只不过有一点点小小的修改，当搜索时会搜索当前类，然后是基类，最后是该类的类(classname.\_\_class\_\_)中查找，也就是<type, 'type'>中查找。

一些内置对象（如list，tuple等）是没有\_\_dict\_\_属性是，所以用户定义的属性不是存储在其中。

### 从函数到方法

```python
>>> class C(object):
...     classattr = "attr on class"
...     def f(self):
...             return "function f"
...
>>> C.__dict__ 1
{'classattr': 'attr on class', '__module__': '__main__',
 '__doc__': None, 'f': <function f at 0x008F6B70>}
 >>> cobj = C()
 >>> cobj.classattr is C.__dict__['classattr'] 2
 True
 >>> cobj.f is C.__dict__['f'] 3
 False
 >>> cobj.f 4
 <bound method C.f of <__main__.C instance at 0x008F9850>>
 >>> C.__dict__['f'].__get__(cobj, C) 5
 <bound method C.f of <__main__.C instance at 0x008F9850>>

 ```

* 1 有两个类属性，一个是字符串'classattr', 一个是函数'f'。
* 2 通过对象访问属性'classattr'时和我们所期望的一样，该属性是从类的\_\_dict\_\_中查找到的。
* 3 但是函数却出乎我们的意料，为什么？
* 4 cobj.f看起来是一个不同的对象（bound method是一个可调用的对象），当我们通过cobj.f()调用该对象时会自动传递cobj作为第一个参数传递给该函数。
* 5 当Python解释器在类的\_\_dict\_\_中查到了所需要的对象，但是这个对象拥有\_\_get\_\_方法。Python不会直接返回这个对象，而是调用这个这个\_\_get\_\_方法，然后返回调用后的结果，调用该方法时会将实例作为第一个参数，而类作为第二个参数。

只有当\_\_get\_\_方法出现时才会将一个普通的函数转换为绑定的方法（bound method）。任何人都可以将一个带有\_\_get\_\_方法的对象放到类的\_\_dict\_\_中，然后通过该类的实例调用该对象。拥有\_\_get\_\_方法的对象称为描述符（Descriptors），描述符有很多用处。

### 创建一个描述符

任何带有\_\_get\_\_，\_\_set\_\_，\_\_delete\_\_方法的对象都是一个描述符，其中\_\_get\_\_方法是必须的，而另外两个是可选的。一个空的描述符如下面所示。

```python
class Desc(object):
    "A descriptor example that just demonstrates the protocol"
    
    def __get__(self, obj, cls=None): 1
        pass

    def __set__(self, obj, val): 2
        pass

    def __delete__(self, obj): 3
        pass
```
* 1 当属性被读取的时候，该方法被调用
* 2 当属性被赋值的时候，该方法被调用
* 3 当属性被删除的时候，该方法被调用

## 方法解析顺序

## 用法

## 参考文档

