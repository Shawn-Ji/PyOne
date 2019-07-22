#!/etc/bash

#11.20
del_rubbish(){
    python -c "from function import *;mon_db.down_db.delete_many({});"
}

#2019.01.10
update_sp(){
    ps -aux | grep supervisord | awk '{print "kill -9 " $2}'|sh
    rm -rf supervisord.conf
    cp supervisord.conf.sample supervisord.conf
    supervisord -c supervisord.conf
}

#2019.01.18
update_config(){

    num=`cat self_config.py | grep "balance" | wc -l`
    if [ $num == 0 ]; then
        echo '' >> self_config.py
        echo 'balance="False"' >> self_config.py
    fi

    num=`cat self_config.py | grep "robots" | wc -l`
    if [ $num == 0 ]; then
        echo '' >> self_config.py
        echo 'robots="""
User-agent:  *
Disallow:  /
"""' >> self_config.py
    fi


    num=`cat self_config.py | grep "admin_prefix" | wc -l`
    if [ $num == 0 ]; then
        echo '' >> self_config.py
        echo 'admin_prefix="admin"' >> self_config.py
    fi


    num=`cat self_config.py | grep "thread_num" | wc -l`
    if [ $num == 0 ]; then
        echo '' >> self_config.py
        echo 'thread_num="5"' >> self_config.py
    fi

    num=`cat self_config.py | grep "verify_url" | wc -l`
    if [ $num == 0 ]; then
        echo '' >> self_config.py
        echo 'verify_url="False"' >> self_config.py
    fi


    num=`cat self_config.py | grep "show_redirect" | wc -l`
    if [ $num == 0 ]; then
        echo '' >> self_config.py
        echo 'show_redirect="exe"' >> self_config.py
    fi

    num=`cat self_config.py | grep "show_image" | wc -l`
    if [ $num == 0 ]; then
        echo '' >> self_config.py
        echo 'show_image="bmp,jpg,jpeg,png,gif"' >> self_config.py
    fi

    num=`cat self_config.py | grep "show_video" | wc -l`
    if [ $num == 0 ]; then
        echo '' >> self_config.py
        echo 'show_video="mp4,webm"' >> self_config.py
    fi

    num=`cat self_config.py | grep "show_dash" | wc -l`
    if [ $num == 0 ]; then
        echo '' >> self_config.py
        echo 'show_dash="avi,mpg,mpeg,rm,rmvb,mov,wmv,mkv,asf"' >> self_config.py
    fi

    num=`cat self_config.py | grep "show_audio" | wc -l`
    if [ $num == 0 ]; then
        echo '' >> self_config.py
        echo 'show_audio="ogg,mp3,wav,aac,flac,m4a"' >> self_config.py
    fi

    num=`cat self_config.py | grep "show_code" | wc -l`
    if [ $num == 0 ]; then
        echo '' >> self_config.py
        echo 'show_code="html,htm,php,py,css,go,java,js,json,txt,sh,md"' >> self_config.py
    fi

    num=`cat self_config.py | grep "show_doc" | wc -l`
    if [ $num == 0 ]; then
        echo '' >> self_config.py
        echo 'show_doc="csv,doc,docx,odp,ods,odt,pot,potm,potx,pps,ppsx,ppsxm,ppt,pptm,pptx,rtf,xls,xlsx"' >> self_config.py
    fi

}





#2019.02.15
upgrade_to4(){
    echo '-------------------------------'
    echo '2019.02.15，PyOne升级为4.0版本！！'
    echo '2019.02.15之前安装的PyOne需重新安装！'
    echo '-------------------------------'
}

#2019.02.16
upgrade(){
    num=`ls | grep .install | wc -l`
    if [ $num == 0 ]; then
        touch .install
    fi
    update_config
    yum install gcc libffi-devel python-devel openssl-devel -y
    pip install -r requirements.txt
    which lsof > /dev/null 2>&1
    if [ $? == 0 ]; then
        echo "lsof exist"
    else
        echo "lsof dose not exist"
        yum install lsof -y
    fi
}

change_redirect(){
    sed -i 's/auth.pyone.me/pyoneauth.github.io/' self_config.py
}


restart(){
    supervisorctl -c supervisord.conf restart pyone
}

#执行
upgrade_to4
upgrade
change_redirect

echo "2018.11.20更新版本，修复了磁力链接下载的bug&上传、展示有特殊字符的文件出问题的bug。"
echo "2018.11.21更新版本，优化磁力下载功能-可选下载文件。"
echo "2018.12.04更新版本，优化磁力下载界面"
echo "2018.12.10更新版本，修复特定分享目录后，二级目录设置密码出错的bug"
echo "2018.12.20更新版本，基础设置之后无需重启网站啦！如果你一直有保存之后不生效的问题，那么本次直接重启服务器吧！"
echo "2019.01.10更新版本，1. 修复防盗链失效的bug；2. 优化开机启动脚本。"
echo "2019.01.13更新版本，修复后台修改密码不生效的bug"
echo "2019.01.14更新版本，修复bug"
echo "2019.01.18更新版本，修复bug；添加搜索功能"
echo "2019.01.21更新版本，添加功能：后台直接添加盘符...避免小白添加配置出现各种问题"
echo "2019.01.23更新版本：修复设置了共享目录后设置README/HEAD/密码出错的bug;优化更新文件列表假死的bug"
echo "2019.01.24更新版本：支持设置加密文件夹下的文件；优化UI"
echo "2019.01.28更新版本：支持自定义代码！"
echo "2019.01.29更新版本：支持设置网站标题前缀；支持自定义主题（待更新设计标准）"
echo "2019.01.30更新版本：提交新主题"
echo "2019.02.15更新版本：新增一键卸载PyOne功能！"
echo "2019.02.16更新版本：优化PyOne4.0安装流程！"
echo "2019.02.19更新版本：优化细节"
echo "2019.02.20更新版本：1. 填坑！2. 后台可配置mongo和redis信息；3. 优化离线下载体验；4. 输出日志"
echo "2019.02.21更新版本：修复自定义代码bug"
echo "2019.02.22更新版本：优化离线下载功能（重启网站后任务不中断）"
echo "2019.02.23更新版本：1. 修复上传bug；2. 优化检测机制"
echo "2019.02.26更新版本：优化上传速度！"
echo "2019.02.27更新版本：修复创建文件夹bug"
echo "2019.02.28更新版本：美化500&404页面"
echo "2019.03.05更新版本：重构&优化上传界面"
echo "2019.03.08更新版本：优化逻辑&修复文件夹连级加密失效的bug&添加新主题"
echo "2019.03.14更新版本：后台输出实时日志&&一键升级PyOne"
echo "2019.03.15更新版本：修复bug&优化layui主题&可设置默认排序字段"
echo "2019.03.19更新版本：可自定义默认盘&可设置默认排序方法"
echo "2019.03.22更新版本：可能修复了离线下载一直占用内存的bug"
echo "2019.03.23更新版本：修复网页查看日志后一直驻后台的bug"
echo "2019.03.26更新版本：修复上一个版本带来的新bug"
echo "2019.05.07更新版本：1、修复若干bug，并带来若干bug；2、重磅更新：【网盘搬家（beta）】功能！！"
echo "2019.05.09更新版本：1、修复【网盘搬家】部分bug；2、修复【更新列表】增量更新不起效的bug；3、【更新列表】可选网盘更新啦！"
echo "2019.05.10更新版本：1、新增robots.txt自定义；2、离线下载功能独立出来"
echo "2019.05.11更新版本：1、修复离线下载bug；2、优化离线下载界面体验"
echo "2019.05.21更新版本：修复若干bug"
echo "2019.05.22更新版本：支持自定义后台路径（更安全）"
echo "2019.05.23更新版本：新增负载均衡功能！"
echo "2019.05.24更新版本：支持世纪互联版本onedrive"
echo "2019.05.25更新版本：参考olaindex，视频和音频出错自动加载&每25分钟重新加载一次"
echo "2019.05.28更新版本：修复开启负债均衡之后，文件名有特殊符号播放不了的bug"
echo "2019.05.29更新版本：支持自定义线程数"
echo "2019.05.31更新版本：新增功能：1）下载链接验证开关；优化：1）aria2信息不对时，无法添加任务"
echo "2019.06.13更新版本：新增功能：文件展示设置"
echo "2019.06.14更新版本：稍微完善一下日志记录；分享页面取消token验证；修复开启下载验证之后，后台文件打开失败的bug；新增内嵌窗口"
echo "---------------------------------------------------------------"
echo "更新完成！"
echo "如果网站无法访问，请检查config.py!"
echo "如果一直提示mongodb或者redis未运行，请自行安装lsof"
echo "---------------------------------------------------------------"
echo
echo "PyOne交流群：864996565"
echo "PyOne交流群TG：https://t.me/joinchat/JQOOug6MY11gy_MiXTmqIA"
echo "end"
restart

