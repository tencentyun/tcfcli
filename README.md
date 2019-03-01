This is a local tools for packing and deploying function to SCF.

### Prepare dev environment
#### Prerequisites：
- Python3.6 or Python2(>2.7)
- Window, Linux, macOS with PIP
- Internet for PyPI

Verify Python Version is 3.6 or >2.7 and PIP is available
```bash
$ pip --version
```

Install virtualenv(you can also use python directly, but there we recommand install virtualenv to make sure environment clean)
```bash
$ pip install virtualenv
```

Init develop code and env

```bash
$ git clone http://git.code.oa.com/virt-plat/tcfcli.git
$ cd tcfcli
$ virtualenv --no-site-packages venv
$ source venv/bin/activate
```
Now you can see **'(venv)'**  before your console, if you want quit venv use:
```bash
$ (venv) deactive
```


### Qucick Start

Make sure you are in fam-tools directory and in the **venv** environment(if using virtualenv), then install this tool
```bash
$ (venv) pip install --editable .
eval "$(_TCF_COMPLETE=source tcf)"
```

Afterwards, your command should be available
```bash
$ (venv) tcf --version
TCF, version 0.1.0
```

### 调用(Invoke)
试用版需要手动登陆镜像仓库，命令如下：
```bash
docker login -u 3473058547 -p qcloud6666  ccr.ccs.tencentyun.com
```

然后执行invoke，这里假设invoke的函数为模版中的function1函数
```bash
echo '{"key": 1}' | tcf local invoke -t demo/template.yaml function1 --skip-pull-image
```

### 模拟apigw调用(start-api)
```bash
tcf local start-api -t demo/template.yaml
```

### 打包(package)
```bash
cd demo
tcf package -t template.yaml

# 可选参数： --output-template-file, -o 设置package命令生成的部署模版路径
#           --cos-bucket 打包后的代码同时存储至给定的cos桶中 
``` 
执行package命令后，会在当前目录下生成用于部署(deploy)云函数的模版文件deploy.yaml及打包好的代码文件xxx.zip
template.yaml模版中的`./helloworld`为云函数代码目录而`index.py`为入口代码文件

模版格式详细定义示例如下
```yaml
# template.yaml
Resources:
  MyFunction1: # 云函数名
    Type: 'Tencent::Scf::Function'
    Properties:
      Handler: index.handler
      Runtime: python2.7
      CodeUri: /home/usr/code/helloworld # 也可为相对于模版文件的相对路径
      Description: This is a template function
      MemorySize: 256
      Timeout: 3
      Environment:
        Variables:
          ENV_FIRST: env1
          ENV_SECOND: env2
      VpcConfig:
        VpcId: vpc-xxx
        SubnetId: subnet-xxx
      Events: # 触发器定义
          HelloWorld1: # service_name
              Type: Api # 类型指定我 APIGW触发器
              Properties:
                  Path: /hello
                  Method: get
                  StageName: release # new apigw default value
                  ResponseIntegration: true # default true

# Globals模块中定义的属性会被Resource模块中的属性继承
Globals:
  Function:
    Timeout: 10
```
模版文件中的各属性含义如下

| 属性 | 描述 | 类型 |
| --------- | :--------- | :---------- |
|Handler|入口文件和方法| String |
|Runtime|执行时语言|String|
|CodeUri|代码路径，本地代码所在目录|String|
|Description|函数描述|String|
|MemorySize|运行时内存|Int|
|Timeout|函数执行超时时间(单位s)|Int|
|Environment|环境变量|Map(string to string)|
|VpcConfig|vpc配置|String|



### 部署(deploy)
执行package命令后，得到部署模版(假设为deploy.yaml)，执行如下命令即可部署代码至云函数平台
```bash
#第一次使用时需要输入appid、secretId等信息，按提示操作即可
tcf deploy -t deploy.yaml
```
