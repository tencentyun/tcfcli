# tcf cli

------

## 什么是 tcf

tcf 全称为 tencent cloud function，是腾讯云无服务器云函数 SCF（Serverless Cloud Function）产品的命令行工具。通过 tcf 命令行工具，您可以方便的实现函数打包、部署、本地调试，也可以方便的生成云函数的项目并基于 demo 项目进一步的开发。

tcf 通过一个函数模板配置文件，完成函数及相关周边资源的描述，并基于配置文件实现本地代码及配置部署到云端的过程。

目前 tcf 以开源形式发布，您可以在本项目中查看命令行源代码及更多帮助文档，并可以通过项目 issue 反馈问题。

## 功能特性

通过 tcf 命令行工具，你可以：

* 快速初始化云函数项目
* 在本地开发及测试你的云函数代码
* 使用模拟的 COS、CMQ、Ckafka、API 网关等触发器事件来触发函数运行
* 验证 TCSAM 模板配置文件
* 打包、上传函数代码，创建函数及更新函数配置

## 运行环境

tcf 可以在 Windows、Linux、Mac 上运行。tcf 基于 Python 开发完成，因此在安装及运行前需要系统中安装有 Python 环境。更详细信息可见[安装及配置](https://github.com/tencentyun/tcfcli/blob/master/docs/安装与配置.md)。

## 快速入门


### 安装 tcf

#### 前置依赖

在安装 tcf 前，请确保系统中已经安装好了如下软件：

* Python 2.7+ 或 Python 3.6+
* pip

#### 通过 pip 安装 tcf

通过使用如下命令完成 tcf 安装：

```bash
$ pip install tcf
```

通过执行如下命令及输出确保 tcf 安装已成功：

```bash
$ tcf --version
TCF CLI, version 0.1.0
```

### 配置 tcf

从腾讯云控制台获取到账号的 APPID，SecretId及 SecretKey 信息，并配置到 tcf 中，作为 tcf 调用云 API 时的认证信息。

例如获取到的账号 APPID 为 1253970223，SecretId 和 SecretKey 分别为 AKIxxxxxxxxxx 及 uxxlxxxxxxxx，期望在广州区使用云函数。则通过如下命令完成 tcf 的配置
：

```bash
$ tcf configure set --region ap-guangzhou --appid 1253970223 --secret-id AKIxxxxxxxxxx --secret-key uxxlxxxxxxxx
```

### 初始化模板项目

选择进入到合适的代码目录，例如 `cd ~`。

通过执行如下命令，创建运行环境为 Python 2.7，名称为 testscf 的项目。

```bash
$ tcf init --runtime python2.7 --name testscf
```

此命令会在当前目录下创建 testscf 项目目录。


### 本地触发函数

执行 `$ cd testscf` 进入项目目录。

通过执行如下命令，本地模拟触发函数。

```bash
$ tcf native invoke -t template.yaml --no-event
```

注：当前仅Node.js runtime支持该能力，并且需要升级TCF CLI >= 0.2.0版本。为保证部署云端和本地运行的结果一致，建议本地安装的runtime版本和云端版本保持一致。例如，如在云端使用Node.js 6.10，则本机建议也安装Node.js 6.x版本。

### 打包项目

执行 `$ cd testscf` 进入项目目录。

可以通过 `ls` 命令看到，当前项目目录下包括了 README 说明文档，hello_world 代码目录，template.yaml 配置文件。

通过执行如下打包命令：
```
$ tcf package --template-file template.yaml
```

tcf 会依据 template.yaml 文件内的描述，将 hello_world 代码目录内的代码生成部署程序包，并生成 deploy 配置文件。

此时再次通过 `ls` 命令，可以看到项目目录内多了 deploy.yaml 部署用配置文件，以及类似 `32b29935-1ec1-11e9-be82-9801a7af1801.zip` 的部署包。


### 部署云函数

通过执行如下命令，完成本地代码包及函数配置部署到云端：

```bash
$ tcf deploy --template-file deploy.yaml 
```

运行成功完成部署后，可以通过进入腾讯云云函数的控制台，检查函数是否已经成功部署。



## 详细使用指导

* [快速开始](https://github.com/tencentyun/tcfcli/blob/master/docs/快速开始.md)
* [安装与配置](https://github.com/tencentyun/tcfcli/blob/master/docs/安装与配置.md)
* [初始化示例项目](https://github.com/tencentyun/tcfcli/blob/master/docs/初始化示例项目.md)
* [打包部署](https://github.com/tencentyun/tcfcli/blob/master/docs/打包部署.md)
* [本地调试](https://github.com/tencentyun/tcfcli/blob/master/docs/本地调试.md)
* [测试模板](https://github.com/tencentyun/tcfcli/blob/master/docs/测试模板.md)
* [模板文件](https://github.com/tencentyun/tcfcli/blob/master/docs/模板文件.md)
* [TCSAM说明](https://github.com/tencentyun/tcfcli/blob/master/docs/specs/tencentcloud%20sam%20version%202018-11-11-zh-cn.md)
* [常见问题 FAQ](https://github.com/tencentyun/tcfcli/blob/master/docs/常见问题%20FAQ.md)


