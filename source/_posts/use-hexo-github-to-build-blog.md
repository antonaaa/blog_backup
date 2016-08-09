---
title: hexo + github 搭建博客
date: 2016-07-07 08:51:49
tags: 
- github
- hexo
categories: 博客
---

> hexo是一个基于node.js的静态博客程序，你可以使用markdown语言来编写你的博客，可以使用hexo提供的命令将其转换成生成静态网页，具体转化为何种样式的静态界面，取决于你所选的主题。

<!-- more -->

## hexo安装和发布流程
![Alt hexo安装和发布流程图](use-hexo-guithub-to-build-blog.png)


<font size=4 color="red">我的电脑是osx系统，所以使用`Homebrew`这个包管理工具，如果是linux系统可以使用`apt-get`包管理工具。</font>


### 1.下载Git
- - -
我们要将`hexo`生成的静态网页部署到`github`上，那么自然需要`git`命令将静态网页`push`到`github`上。
使用以下命令下载`git`
```bash
sudo brew install git #osx
sudo apt-get install git #linux
```



### 2.下载node.js
- - -
`hexo`是使用`nodejs`编写的，所以你要安装`nodejs`，`hexo`才能够正常运行。这就好比一个程序是用`Python`写的，你需要下载`Python`解释器才能运行该程序。

使用以下命令下载`nodejs`
```bash
sudo brew install nodejs #osx
sudo apt-get install nodejs #linux
```

安装完`nodejs`应该会顺带着安装`nodejs`的包管理工具`npm`，使用`which npm`来判断有没有安装`npm`，如果没有则使用以下命令安装`npm`。
```bash
sudo brew install npm #osx
sudo apt-get install npm #linux
```


### 3.下载和使用hexo
- - -

使用以下命令安装`hexo`

```bash
sudo npm install -g hexo
```

使用以下命令生成博客的工作目录，以后所有的操作都会在该目录下。
```bash
sudo hexo init blog
cd blog #进入该目录，以后的所有命令都在该目录下执行
```

使用以下命令安装依赖项，会在blog目录中安装node\_modules。
```bash
sudo npm install
```

上面已经完成了hexo的搭建了，接下来只要使用
```
sudo hexo g
```
生成静态文件，然后使用
```
sudo hexo s
```
开启服务器，那么就可以通过`http://localhost:4000` 来访问我们自己的博客了。


### 4.部署到github上
- - -


#### 创建仓库

部署静态网页的仓库对仓库名有要求，比如你`github`的账号是`ABC`，那么你仓库的名字必须是`ABC.github.io`

#### 生成SSH Keys

使用以下命令生成SSH Keys
```bash
ssh-keygen -t rsa -C "这里是你申请Github账号时的邮箱"
#-t rsa 表明使用rsa加密算法
#-C 表明后面的是一个注释，是用来区分公钥是谁的，毕竟公钥一多，公钥对于人来说又不是可读的，所以加个注释好区分。
```

生成密钥之后会`~/`目录下生成`.ssh`目录，且该目录下有`id_rsa`和`id_rsa.pub`两个文件，前者表示私钥，后者表示公钥。

#### 将公钥添加到github

登录`github`，进入settings -> SSH and GPG keys -> New SSH key，然后将`id_rsa.pub`中的内容复制过来。

我们部署时需要将`hexo`生成的静态网页`push`到我们自己的远程的github仓库，而SSH远程访问能够保证安全性，所以github使用这种方式。

#### 配置git
我们在本地使用`git`命令操作`github`时，`git`怎么知道我们操作的是哪个账号呢？所以需要配置我们的用户名和邮箱

```bash
git config --global user.name"这里是你申请Github账号时的name"
git config --global user.email"这里是你申请Github账号时的邮箱"
```

使用以下命令查看是否能够SSH成功github
```bash
ssh -T git@github.com
#出现以下消息表示成功了
i gzmviavia! You've successfully authenticated, but GitHub does not provide shell access.
```

#### 部署
修改博客根目录下的`_config.yml`文件，修改文件的最后为
```bash
deploy:
  type: git #或者填github
  repo: https://github.com/gzmviavia/gzmviavia.github.io.git #这里要修改成你自己的仓库名
  branch: master
```

最后使用
```bash
sudo hexo d
```
就可以将项目部署上github上了。

也许部署时会出现以下错误
```
ERROR Deployer not found: git 或者 ERROR Deployer not found: github
```

解决方案是
```
sudo npm install hexo-deployer-git --save
```


其实部署的只是由hexo生成的静态页面，我们书写的markdown还是在本地存储的，所以不要以为你部署到github上你就不用备份本地的博客了。

还需要对博客文件进行备份，具体如何备份见 [备份 hexo 博客](/2016/08/07/backup-hexo)
