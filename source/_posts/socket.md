---
title: python socket编程 
date: 2016-08-25 20:36:01
tags:
- 计算机网络
- socket
- python
categories:
- 计算机网络
- python
---

socket是网络编程的基础，socket为我们提供了操纵TCP和UDP的接口。所以要先学好TCP/IP理论，然后学习socket编程，然后再根据socket提供的各种API接口，返回去看TCP/IP理论，从而加深对TCP/IP理论的理解。

<!-- more -->
socket是应用层与TCP/IP协议族通信的中间软件抽象层，它是一组接口，它把复杂的实现隐藏在了接口后面，用户通过接口让socket去组织数据，以符合指定的协议。如下图，用户进程通过socket抽象层，操纵着各种协议。

![socket](socket.png)
## 创建socket对象
python的`socket`模块为我们提供了socket编程相关的API，使用该模块中的`socket.socket(family, type, protocol)`函数创建一个socket对象。
其中family用来指明地址家族（address family），可用的值有：
+ `socket.AF_UNIX`，表明使用在同一台机器上的进程间通信的TCP和UDP通信。
+ `socket.AF_INET`，表明使用IPV4协议的TCP和UDP通信。
+ `socket.AF_INET6`，表明使用IPV4协议的TCP和UDP通信。

type用来指明socket的类型，可以用的值有：
+ `socket.SOCK_STREAM`，表明这个套接字是使用TCP进行通信。
+ `socket.DGRAM`，表明这个套接字是使用UDP进行通信。
+ `socket.RAW`，表明这是一个原始套接字，使用该套接字可以自己构造TCP头，IP头，数据链路层协议头等。黑客就是使用该套接字伪造报文的。

protocol用来指明协议类型，一般只有type是`socket.RAW`时才需要指定，表明需要发送/接收什么协议类型的包。

所以要创建一个TCP类型的`socket`对象可以这么做
```python
sock  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
```
## 设置socket选项
## 绑定地址和端口号
进程可以使用`bind`函数把一个特定的IP地址绑定到套接字上，不过这个IP地址必须是本机的网络接口之一。
+ 对于TCP客户端来说，这就为该套接字上发送的IP数据报指定了源IP地址。不过TCP客户端通常都不把IP地址绑定到它的套接字上，当套接字连接时，内核根据所用的外出网络的接口来选择源IP地址。也就是说客户端的socket通常都不需要调用`bind`函数。
+ 对于TCP服务器来说，这就限定了该套接字只接收那些目的地址为这个IP地址的客户连接。如果TCP服务器没有把IP地址绑定到它的套接字上，那么就把客户发送的SYN的目的地址作为服务器的源IP地址。

```python
#sock.bind((HOST, PORT))
sock.bind(('192.168.1.1', 5678))
```
参数PORT可以为0，为0代表让内核为套接字选择一个临时端口号，为了获得这个端口号，要使用`getsockname`。

```
sock.bind(('192.168.1.1', 0))
print sock.getsockname()
```

调用`bind`函数可以指定IP地址和端口，也可以都不指定，各种结果如图所示。

![socket\_bind](socket_bind.png)

## 监听地址和端口号
`listen(backlog)`函数仅由TCP服务器调用，一个套接字调用`listen`函数之后，该套接字就从一个未连接套接字变成了被动套接字，该被动套接字能够接受远程套接字的连接请求。


TCP为监听套接字维护两个队列，分别是未完成连接队列和已完成连接队列。
+ 未完成连接队列，每个SYN分组对于其中的一项，这些SYN分组是由客户端发来的，服务器正等待完成相应的TCP三次握手的过程，这些套接字都处于**SYN_RCVD**状态。
+ 已完成连接队列，每个已经完成三次握手的客户对应其中一项，这些套接字处于**ESTABLISHED**状态。
![socket\_listen](socket_listen.png)

`backlog`参数曾经被规定为**两个队列总和的最大值**，但是现在的`backlog`参数是指**已完成队列的最大值**。
`backlog`参数如果是两个队列的最大值，那么就会发生这么一种情况，黑客以高速率向受害主机发送SYN报文，那么未完成队列就是满的，当队列是满的时候就会丢弃那些发来的SYN报文，所以这种攻击叫做拒绝服务（denial service）攻击。
所以现在的`backlog`参数是指已完成队列的最大值，对于已完成连接数目做出限定的目的在于：在监听某个套接字的应用进程因为某种原因不调用`accept`接受已完成连接时，防止内核在该套接字上继续接受新的连接请求。

`backlog`的最大值是5，每当监听套接字调用`accept`函数时，就从已完成连接队列的队首取出一个已完成的连接。
```python
sock.listen(5)
```

## 客户端连接服务器

TCP客户使用使用`connect`函数来与TCP服务器建立连接，即激发了三次握手过程，该函数在建立成功或者发送错误时返回。
```python
#sock.connect((HOST, PORT))
sock  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('192.168.1.1', 5678))
```

## 服务器获取远程连接的socket
TCP服务器使用`accept`从已完成连接队列队首返回一个已完成的连接，如果队列为空，那么进程会被阻塞（如果套接字是使用默认的阻塞模式）。
如果`accept`成功，返回与客户端连接的socket，已经客户端的地址。
```python
client_sock, client_addr = sock.accept()
```
## 接收数据

+ `recv(bufsize)` : 从socket的接收缓冲中读取数据，最多读取bufsize个字节的数据，如果接收缓冲区中没有数据，那么默认会阻塞。
+ `recvfrom(bufsize)` : 同`recv(bufsize)`，不同返回值是一个二元组`(data, address)`，address也是一个二元组(HOST, PORT)，即套套接字另一端主机的地址和端口

## 发送数据
+ `send(data)` : 发送数据给套接字另一端的主机，如果data比发送缓冲区的还大，那么会丢弃多余的数据。该函数返回已发送的字节数。 所以应用进程必须自己检查是否所有的数据都发送出去了。
+ `sendall(data)` : 该函数会把所有的数据都发送出去了才返回。
+ `sendto(data,address)` : 上面的两个方法都要求套接字已经和远端的主机建立了连接，而这个方法要求没有建立连接，所有要在参数中指定远端主机的address，所以使用该函数的时候会根据参数address建立连接，然后之后的行为和函数`recv(data)`一样。


## 关闭远程连接的socket
A使用`close`函数会关闭连接，如果套接字缓冲区中还有数据没有发送，那么就蝶祈，然后发出FIN报文，而对方B会回应一个ACK报文。那么此后A到B这一方向的连接就关闭了，但是B到A这一方向的连接却没有关闭。
此时，该连接就是一个半连接，也就是说B可以继续向A发送数据，按照TCP/IP协议，此时A也应该可以继续接收消息。但是如果`close`之后再调用`recv`函数会引发一个`socket.error: [Errno 9] Bad file descriptor`错误。

如果想在连接变成半连接时还能够接收数据，则应该调用`shutdown(socket.SHUT_WR)`，该函数可以关闭连接的写半部（使用SHUT\_WR参数），可以关闭连接的读半部（使用SHUT\_RD参数），也可以同时关闭读半部和写半部（使用SHUT\_RDWD参数）。
+ 使用SHUT\WR参数关闭写半部时，会发送缓冲区中尚未发送的数据，而不会像`close`函数那样丢弃。关闭写半部后，就不能使用该套接字发送数据了。
+ 使用SHUT\_RD参数关闭读半部并不会发出FIN报文给报文，关闭读半部后，该套接字会丢弃当前接收缓冲区中的所有数据，之后会对对端发来的数据进行确认，但是紧接着就丢弃这些数据，并不会放到缓冲区中，对设置了读半部的的套接字调用`recv`函数并不会阻塞，而是立即返回空。

<br />
参考：
[linux下RAW SOCKET](http://blog.csdn.net/firefoxbug/article/details/7561159)
[Linux raw socket](http://www.cnblogs.com/uvsjoh/archive/2012/12/31/2840883.html)
