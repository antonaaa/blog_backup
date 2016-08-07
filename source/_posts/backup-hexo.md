---
title: 备份 hexo 博客
date: 2016-08-07 15:51:24
tags: hexo
categories:
---

将`hexo`部署到`github`上时，部署的只是生成的静态页面，我们所书写的`markdown`，还有主题等还是存储在本地的，所以一旦本地的东西没有了，那么博客基本上就GG了，所以还需要在`github`开辟一个新的仓库来备份这些东西。

<!-- more -->

## 上传备份
- - -
### 1. 初始化本地仓库

删除主题目录下的.git文件，然后进行初始化仓库
```bash
git init
```

博客根目录下的`.gitignore`文件，当我们使用`git`时，该文件中所指定的文件的变化不会被`git`所追踪的。

该文件中的内容为
```bash
.DS_Store #osx系统的隐藏文件
db.json
*.log
node_modules #node 的模块文件，太大了，所以我们不push
public/ #生成的静态文件，也是没用的，所以不用push
.deploy*/ #部署文件，也是不需要push
```
使用以下命令进行第一次提交
```bash
git add .
git commit -m ""
```

### 2. 同步至远程仓库 

将本地的仓库与远程的仓库进行同步，我在`github`上创建的仓库为`https://github.com/gzmviavia/blog_backup`
执行以下命令就能将我们本地的博客文件都同步到`github`远程仓库了。
以后每写完一篇文章，除了部署外，还需要对博客文件进行备份。
```
git remote add origin https://github.com/gzmviavia/blog_backup.git
git push -u origin master
```

## 下载备份
- - -

使用下面的命令将`githut`的仓库拉到本地
```
git clone https://github.com/gzmviavia/blog_backup  blog
```
由于我们备份的时候没有备份`node_modules`这个模块文件，所以需要重新下载。

使用下面的命令进行下载
```
sodu npm install
```

下载完之后生成静态文件，然后开启服务器就可以访问了。
```
hexo g
hexo s
```


## 参考
[Hexo在两台电脑间的操作流程](http://sufaith.com/2016/02/27/Hexo%E8%BF%81%E7%A7%BB/)
