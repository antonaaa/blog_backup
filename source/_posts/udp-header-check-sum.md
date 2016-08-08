---
title: UDP首部检验和
date: 2016-08-08 23:02:38
tags:
- 运输层
- UDP
categories: 计算机网络
---


## UDP首部检验和的计算规则
> ARP协议，IP协议首部的检验和计算时都是先将`checksum`字段置为0，然后对首部字段进行16位反码求和，并不会覆盖数据部分。而UDP计算检验和时会对UDP伪首部、UDP首部、UDP数据部分都进行16位反码求和，由于数据部分可能是奇数位，所以如果数据部分为奇数位时，为了计算检验和会在最后增加填充字节0，这只是为了计算检验和，并不会被发送。

<!-- more -->

	为什么要加上伪首部然后计算检验和呢？

所需要计算检验和的字段如下图所示。

![UDP首部检验和字段](udp_check_sum_header.png)


## 发送UDP数据报
使用以下代码发送一个UDP数据包，ip地址和端口可以随便填，只要不填本地地址就好了，因为自己向自己发的数据是不会经过网卡的，所以会抓不到包。

```python
#!/usr/bin/python2.7
#coding:utf-8
import socket

ip = '12.34.56.78'
port = 80
addr = (ip, port)

udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.sendto('dat', addr) #特意发送奇数个字节的数据

```

## 抓取UDP数据报
使用wireshark抓到该UDP报，包的具体数据如下：

![](UDP_packet.png)

可以看到UDP的首部检验和为`0x58dx`

## 计算首部检验和
为了验证UDP首部检验码是怎么计算的，使用以下代码对首部检验和进行计算
```cpp
#include <stdio.h>

int check_sum(unsigned short *arr, int n){
	int sum = 0;
	for(int i=0; i<n; ++i){
		arr[i] = ~arr[i];
		sum += arr[i];
		sum = (sum>>16) + (sum&0xffff);
	}
	return sum;
}
int main()
{
	unsigned short arr[100];
	arr[0] = 0xc8d5; //源端口
	arr[1] = 0x0050; //目的端口
	arr[2] = 0x000b; //udp长度，8个字节的首部 + 4个字节的数据
	arr[3] = 0x0000; //checksum
	arr[4] = 0x6461; //数据部分
	arr[5] = 0x7400; //在最后增加填充字节0

	//伪首部
	arr[6] = 0xc0a8; //源ip
	arr[7] = 0x0064;
	arr[8] = 0x0c22; //目的ip
	arr[9] = 0x384e;
	arr[10] = 0x0011; // 0 + 8位协议
	arr[11] = 0x000b; //udp长度
	int n = 12;
	printf("%x\n",check_sum(arr, n));
	return 0;
}


```

运行该代码后，果然发现检验和是`0x58d4`

注：使用Python发送UDP是因为Python发送数据报简单，使用C++计算检验和是因为C++位运算方便，Python位运算还需要用到struct包，太麻烦了。



