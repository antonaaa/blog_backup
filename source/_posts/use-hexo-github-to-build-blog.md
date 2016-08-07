---
title: hexo + github 搭建博客
date: 2016-08-07 08:51:49
tags: 
- github
- hexo
---

> hexo是一个基于node.js的静态博客程序，你可以使用markdown语言来编写你的博客，你可以使用hexo提供的命令将其转换成生成静态网页，hexo会根据主题模板自动将你的文章转为网页。

<!-- more -->
## hexo安装和发布流程
![Alt hexo安装和发布流程图](http://obil5saf9.bkt.clouddn.com/20160808hexo_flow)
### 1.下载Git
- - -
我的电脑是osx系统，所以使用brew这个包管理工具，如果是linux系统可以使用apt-get包管理工具。

osx系统使用以下命令下载git
```bash
sudo brew install git
```

linux系统使用以下命令下载git
```bash
sudo apt-get install git
```



### 2.下载node.js
- - -
hexo是使用node.js编写的，所以你要安装node.js，hexo才能够正常运行。

osx系统使用以下命令下载node.js
```bash
sudo brew install nodejs
```

linux系统使用以下命令下载node.js
```bash
sudo apt-get install nodejs
```

### 3.下载hexo
- - -
#### 1.安装hexo
使用以下命令安装hexo
```bash
sudo npm install -g hexo
```

使用以下命令生成博客的工作目录，以后所有的操作都会在该目录下
```bash
sudo hexo init blog
cd blog #进入该目录，以后的所有命令都在该目录下执行
```

使用以下命令安装依赖项，会在blog目录中安装node\_modules
```bash
sudo npm install
```

#### 2.使用hexo
上面已经完成了hexo的搭建了，接下来只要使用
```
hexo g
```
生成静态文件，然后使用
```
hexo s
```
开启服务器，那么就可以通过http://localhost:4000 来访问我们自己的博客了。
hexo常用的命令有：
```bash
hexo g #生成静态文件
hexo s #开启服务器
hexo d #将.deploy_git部署到你的github
hexo new "postname" #新建文章
hexo new page "pagename" #新建页面

```
### 4.部署到github上
- - -
使用以下命令生成SSH Keys
```bash
ssh-keygen -t rsa -C"这里是你申请Github账号时的邮箱"
```

将~/.ssh/id\_rsa.pub中的公钥添加到github

配置git
```bash
git config --global user.name"这里是你申请Github账号时的name"
git config --global user.email"这里是你申请Github账号时的邮箱"
```
使用以下命令查看是否能够SSH成功github
```bash
ssh-T git@github.com
```

修改博客根目录下的\_config.yml文件，修改文件的最后为
```bash
deploy:
  type: git
  repo: https://github.com/gzmviavia/gzmviavia.github.io.git #这里要修改成你自己的参考名
  branch: master
```

最后使用
```bash
hexo d
```
就可以将项目部署上github上了。
其实部署的只是由hexo生成的静态页面，我们书写的markdown还是在本地存储的，所以不要以为你部署到github上你就不用备份本地的博客了。
