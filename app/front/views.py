#-*- coding=utf-8 -*-
import time
import datetime
from flask import render_template,redirect,abort,make_response,jsonify,request,url_for,Response,send_from_directory
from flask_sqlalchemy import Pagination
from ..utils import *
from ..extend import *
from . import front
from alipay import AliPay

alipay = AliPay(
    appid=GetConfig('APPID'),
    app_notify_url=GetConfig('notify_url'),  # 默认回调url
    app_private_key_string=GetConfig("private_key"),
    alipay_public_key_string=GetConfig("public_key"),
    sign_type="RSA2"
)


################################################################################
###################################前台函数#####################################
################################################################################
@front.before_request
def before_request():
    bad_ua=['Googlebot-Image','FeedDemon ','BOT/0.1 (BOT for JCE)','CrawlDaddy ','Java','Feedly','UniversalFeedParser','ApacheBench','Swiftbot','ZmEu','Indy Library','oBot','jaunty','YandexBot','AhrefsBot','MJ12bot','WinHttp','EasouSpider','HttpClient','Microsoft URL Control','YYSpider','jaunty','Python-urllib','lightDeckReports Bot','PHP','vxiaotou-spider','spider']
    global referrer
    try:
        ip = request.headers['X-Forwarded-For'].split(',')[0]
    except:
        ip = request.remote_addr
    try:
        ua = request.headers.get('User-Agent')
    except:
        ua="null"
    if sum([i.lower() in ua.lower() for i in bad_ua])>0:
        return redirect('http://www.baidu.com')
    # print '{}:{}:{}'.format(request.endpoint,ip,ua)
    referrer=request.referrer if request.referrer is not None else 'no-referrer'


@front.errorhandler(500)
def page_not_found(e):
    # note that we set the 500 status explicitly
    msg,status=CheckServer()
    return render_template('error.html',msg=msg,code=500), 500

@front.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    msg,status=CheckServer()
    return render_template('error.html',msg=msg,code=404), 404


@front.route('/favicon.ico')
def favicon():
    resp=MakeResponse(send_from_directory(os.path.join(config_dir, 'app/static/img'),'favicon.ico',mimetype='image/vnd.microsoft.icon'))
    return resp

@front.route('/<path:path>',methods=['POST','GET'])
@front.route('/',methods=['POST','GET'])
@limiter.limit("200/minute;50/second")
def index(path=None):
    balance=eval(GetConfig('balance'))
    if path is None:
        path='{}:/'.format(GetConfig('default_pan'))
    path=urllib.unquote(path).split('?')[0]
    if not os.path.exists(os.path.join(config_dir,'.install')):
        resp=redirect(url_for('admin.install',step=0,user=GetConfig('default_pan')))
        return resp
    try:
        user,n_path=path.split(':')
    except:
        if path==GetConfig('admin_prefix'):
            return redirect(url_for('admin.setting'))
        else:
            return MakeResponse(abort(404))
    if balance:
        if user!=GetConfig('default_pan'):
            return MakeResponse(abort(404))
    if n_path=='':
        path=':'.join([user,'/'])
    page=request.args.get('page',1,type=int)
    image_mode=GetCookie(key='image_mode',default=0)
    sortby=GetCookie(key='sortby',default=GetConfig('default_sort'))
    order=GetCookie(key='order',default=GetConfig('order_m'))
    action=request.args.get('action','download')
    token=request.args.get('token')
    data,total = FetchData(path=path,page=page,per_page=50,sortby=sortby,order=order,action=action,dismiss=True)
    #是否有密码
    password,_,cur=has_item(path,'.password')
    if request.method=="GET":
        if not path.endswith(".mp4"):
            pass
        else:
            # print(request.host)
            if GetConfig('vip_password') == "" or request.cookies.get("password") == GetConfig('vip_password'):
                pass
            else:
                if request.host == "v.zhiboluzhi.cn":
                    master_url = "http://zhiboluzhi.cn"
                    master_txt = "点我, 在云录制中赞助主播后获取视频密码"
                else:
                    master_url = "http://show.zhiboluzhi.cn"
                    master_txt = "点我, 在云录制-秀场专区中注册成为会员后获取视频密码"
                resp=MakeResponse(render_template('theme/{}/password.html'.format(GetConfig('theme')),path=path,cur_user=user, master_url=master_url, master_txt=master_txt))
                return resp
    md5_p=md5(path)
    has_verify_=has_verify(path)
    if request.method=="POST":
        password1=request.form.get('password')
        if password1==GetConfig('vip_password'):
            resp=show(data['id'],data['user'],action,token=token)
            # resp.delete_cookie(md5_p)
            resp.set_cookie("password",password1)
            return resp
        else:
            return "密码错误"
    if password!=False:
        if (not request.cookies.get(md5_p) or request.cookies.get(md5_p)!=password) and has_verify_==False:
            if total=='files' and GetConfig('encrypt_file')=="no":
                if GetConfig("verify_url")=="True" and action not in ['share','iframe']:
                    if token is None:
                        return abort(403)
                    elif VerifyToken(token,path):
                        return show(data['id'],data['user'],action,token=token)
                    else:
                        return abort(403)
                else:
                    return show(data['id'],data['user'],action,token=token)
            resp=MakeResponse(render_template('theme/{}/password.html'.format(GetConfig('theme')),path=path,cur_user=user))
            return resp
    if total=='files':
        if GetConfig("verify_url")=="True" and action not in ['share','iframe']:
            if token is None:
                return abort(403)
            elif VerifyToken(token,path):
                return show(data['id'],data['user'],action,token=token)
            else:
                return abort(403)
        else:
            return show(data['id'],data['user'],action,token=token)
    readme,ext_r=GetReadMe(path)
    head,ext_d=GetHead(path)
    #参数
    all_image=False if sum([file_ico(i)!='image' for i in data])>0 else True
    pagination=Pagination(query=None,page=page, per_page=50, total=total, items=None)
    if path.split(':',1)[-1]=='/':
        path=':'.join([path.split(':',1)[0],''])
    resp=MakeResponse(render_template('theme/{}/index.html'.format(GetConfig('theme'))
                    ,pagination=pagination
                    ,items=data
                    ,path=path
                    ,image_mode=image_mode
                    ,readme=readme
                    ,ext_r=ext_r
                    ,head=head
                    ,ext_d=ext_d
                    ,sortby=sortby
                    ,order=order
                    ,cur_user=user
                    ,all_image=all_image
                    ,endpoint='.index'))
    resp.set_cookie('image_mode',str(image_mode))
    resp.set_cookie('sortby',str(sortby))
    resp.set_cookie('order',str(order))
    return resp

@front.route('/file/<user>/<fileid>/<action>/<token>')
def show(fileid,user,action='download',token=None):
    if token is None:
        token=request.args.get('token')
    path=GetPath(fileid)
    name=GetName(fileid)
    ext=name.split('.')[-1].lower()
    url=request.url.replace(':80','').replace(':443','').encode('utf-8').split('?')[0]
    url='/'.join(url.split('/')[:3])+'/'+urllib.quote('/'.join(url.split('/')[3:]))
    if GetConfig("verify_url")=="True":
        url=url+'?token='+GenerateToken(path)
        if action not in ['share','iframe']:
            if token is None:
                return abort(403)
            elif VerifyToken(token,path)==False:
                return abort(403)
    if request.method=='POST' or action in ['share','iframe']:
        InfoLogger().print_r(u'share page:{}'.format(path))
        if ext in GetConfig('show_redirect').split(','):
            downloadUrl,play_url=GetDownloadUrl(fileid,user)
            resp=MakeResponse(redirect(downloadUrl))
        elif ext in GetConfig('show_doc').split(','):
            downloadUrl,play_url=GetDownloadUrl(fileid,user)
            url = 'https://view.officeapps.live.com/op/view.aspx?src='+urllib.quote(downloadUrl)
            resp=MakeResponse(redirect(url))
        elif ext in GetConfig('show_image').split(','):
            if action=='share':
                resp=MakeResponse(render_template('theme/{}/show/image.html'.format(GetConfig('theme')),url=url,path=path,cur_user=user,name=name))
            else:
                resp=MakeResponse(render_template('show/image.html'.format(GetConfig('theme')),url=url,path=path,cur_user=user,name=name))

        elif ext in GetConfig('show_video').split(','):
            if action=='share':
                resp=MakeResponse(render_template('theme/{}/show/video.html'.format(GetConfig('theme')),url=url,path=path,cur_user=user,name=name))
            else:
                resp=MakeResponse(render_template('show/video.html'.format(GetConfig('theme')),url=url,path=path,cur_user=user,name=name))
        elif ext in GetConfig('show_dash').split(','):
            if action=='share':
                resp=MakeResponse(render_template('theme/{}/show/video2.html'.format(GetConfig('theme')),url=url,path=path,cur_user=user,name=name))
            else:
                resp=MakeResponse(render_template('show/video2.html'.format(GetConfig('theme')),url=url,path=path,cur_user=user,name=name))
        elif ext in GetConfig('show_audio').split(','):
            if action=='share':
                resp=MakeResponse(render_template('theme/{}/show/audio.html'.format(GetConfig('theme')),url=url,path=path,cur_user=user,name=name))
            else:
                resp=MakeResponse(render_template('show/audio.html'.format(GetConfig('theme')),url=url,path=path,cur_user=user,name=name))
        elif ext in GetConfig('show_code').split(','):
            content=common._remote_content(fileid,user)
            if action=="share":
                resp=MakeResponse(render_template('theme/{}/show/code.html'.format(GetConfig('theme')),content=content,url=url,language=CodeType(ext),path=path,cur_user=user,name=name))
            else:
                resp=MakeResponse(render_template('show/code.html'.format(GetConfig('theme')),content=content,url=url,language=CodeType(ext),path=path,cur_user=user,name=name))
        elif name=='.password':
            resp=MakeResponse(abort(404))
        else:
            downloadUrl,play_url=GetDownloadUrl(fileid,user)
            resp=MakeResponse(redirect(downloadUrl))
        return resp
    if name=='.password':
        resp=MakeResponse(abort(404))
    if 'no-referrer' in GetConfig('allow_site').split(',') or sum([i in referrer for i in GetConfig('allow_site').split(',')])>0:
        downloadUrl,play_url=GetDownloadUrl(fileid,user)
        if not downloadUrl.startswith('http'):
            return MakeResponse(downloadUrl)
        else:
            resp=MakeResponse(redirect(play_url))
    else:
        resp=MakeResponse(abort(404))
    return resp



@front.route('/py_find/<key_word>')
def find(key_word):
    page=request.args.get('page',1,type=int)
    ajax=request.args.get('ajax','no')
    image_mode=request.args.get('image_mode')
    sortby=request.args.get('sortby')
    order=request.args.get('order')
    action=request.args.get('action','download')
    data,total=FetchData(path=key_word,page=page,per_page=50,sortby=sortby,order=order,dismiss=True,search_mode=True)
    pagination=Pagination(query=None,page=page, per_page=50, total=total, items=None)
    if ajax=='yes':
        retdata={}
        retdata['code']=0
        retdata['msg']=""
        retdata['total']=total
        retdata['data']=[]
        for d in data:
            info={}
            if d['type']=='folder':
                info['name']='<a href="'+url_for('.index',path=d['path'])+'">'+d['name']+'</a>'
            else:
                info['name']='<a href="'+url_for('.index',path=d['path'],action='share')+'" target="_blank">'+d['name']+'</a>'
            info['type']=d['type']
            info['lastModtime']=d['lastModtime']
            info['size']=d['size']
            info['path']=d['path']
            info['id']=d['id']
            retdata['data'].append(info)
        return jsonify(retdata)
    resp=MakeResponse(render_template('theme/{}/find.html'.format(GetConfig('theme'))
                    ,pagination=pagination
                    ,items=data
                    ,path='/'
                    ,sortby=sortby
                    ,order=order
                    ,key_word=key_word
                    ,cur_user='搜索:"{}"'.format(key_word)
                    ,endpoint='.find'))
    resp.set_cookie('image_mode',str(image_mode))
    resp.set_cookie('sortby',str(sortby))
    resp.set_cookie('order',str(order))
    return resp


@front.route('/create_order')
def create_order():
    print(GetConfig('vip_price'))
    day = int(datetime.datetime.now().strftime('%d'))
    index = str(time.time())
    left = (31.0 - day) / 31.0
    price = max(round(left * int(GetConfig('vip_price'))), 1)

    order = {
        "index": index,
        "day": day,
        "price": price,
        "has_confirmed": False
    }
    mon_db.order.insert_one(order)
    resp=MakeResponse(render_template('theme/{}/create_order.html'.format(GetConfig('theme'))
                    ,index=index
                    ,price=price
                    ,day=day))
    return resp


@front.route('/pay/<index>')
def pay(index):
    price = mon_db.order.find_one({"index":index}).get("price")
    r = alipay.api_alipay_trade_precreate(
        subject="云录制会员",
        out_trade_no="{}and{}".format("onedrive", index),
        total_amount=price
    )
    j = r
    qr_url = j["qr_code"]
    payPicUrl = "http://zhiboluzhi.cn/generate_Image?qr_url={}".format(qr_url)
    resp=MakeResponse(render_template('theme/{}/pay.html'.format(GetConfig('theme'))
                    ,payPicUrl=payPicUrl
                    ,my_orderId=index))
    return resp


@front.route('/check_order/<order_id>')
def check_order(order_id):
    order = mon_db.order.find_one({"index":order_id})
    if order.get("has_confirmed"):
        return GetConfig('vip_password')
    else:
        return "False"


@front.route('/alipay_callback', methods=['POST','GET'])
def alipay_callback():
    print(request.method)
    if request.method=='POST':
        print("request.form")
        print(request.form)
        print('request.form.get("out_trade_no")')
        print(request.form.get("out_trade_no"))
        print("request.data.decode")
        print(request.data.decode("utf8"))

        j = request.form

        outOrderId = j.get("out_trade_no", None)
        if outOrderId:
            if outOrderId.split("and")[0] != "onedrive":
                return "client is not me"

        try:
            outOrderId = outOrderId.split("and")[-1]
            order = mon_db.order.find_one({"index":outOrderId})
        except:
            print("cant find")
            return "cant find"
        if order.get("has_confirmed"):
            print("has confirmed")
            return "has confirmed"

        if j.get("trade_status") != 'TRADE_SUCCESS':
            return "not pay"
        new_value = {}
        new_value['has_confirmed'] = True
        mon_db.order.update_many({'index':outOrderId},{'$set':new_value})

        return "success"

    return "404"

@front.route('/robots.txt')
def robot():
    resp=GetConfig('robots')
    resp=MakeResponse(resp)
    resp.headers['Content-Type'] = 'text/javascript; charset=utf-8'
    return resp

