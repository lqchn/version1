from django.shortcuts import render, render_to_response

# Create your views here.



#my views import here
from django.contrib import auth

from django.contrib.auth.models import User

from django.http import HttpResponse, HttpResponseRedirect

from django.views.decorators.csrf import csrf_exempt


from UserClient.models import UserClient, Photo, Comment, Follow

from UserClient.forms import RegisterUserForm, LoginUserForm, UploadPhotoForm, UserComment, UserChangeInfo

import json

from PIL import Image

import os

import datetime

#register views
def register(request):
    return render_to_response('register/register.html')


#changed
@csrf_exempt
def user_register(request):
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            try:
                u = User.objects.create_user(username=request.POST['username'], password=request.POST['password'])
                user = UserClient.objects.create(user=u, nickname=request.POST['nickname'], signature='I have nothing to say...', headshot='/static/images/defaultheadshot.png')
                return HttpResponseRedirect('/login/')
            except:
               return HttpResponseRedirect('register/register.html')
        else:
            return HttpResponse('register/register.html')

    else:
        return HttpResponse('register/register.html')


#login views
def login(request):
    return render_to_response('login/login.html')

@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        form = LoginUserForm(request.POST)
        if form.is_valid():
            user = auth.authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None and user.is_active:
                auth.login(request, user)
                return HttpResponseRedirect('/index/')
            else:
                return render(request, 'login/login.html')
        else:
            return render(request, 'login/login.html')
    return render(request, 'login/login.html')


#index views
def index(request):
    return render(request, 'index/index.html')

def user_index(request):
    u_id = request.user.id
    user = UserClient.objects.get(user_id = u_id)
    m = {
        'nickname': user.nickname,
        'signature': user.signature,
        'headshot': user.headshot
    }
    return HttpResponse(json.dumps(m))


#pages views;
def pages(request):
    return render(request, 'pages/pages.html' )

@csrf_exempt
def upload_pic(request):
    if request.method == 'POST':
        form = UploadPhotoForm(request.POST, request.FILES)
        #if form.is_valid():
        user = UserClient.objects.get(user_id = request.user.id)
        ip_addr = request.META['REMOTE_ADDR']
        #description = form.cleaned_data['description']
        #upload_photo = form.cleaned_data['upload_photo']
        description = request.POST['description']
        upload_photo = request.FILES['upload_photo']
        upload_date = datetime.datetime.now()
        img = Photo.objects.create(description=description, ip_addr=ip_addr, praise=0, upload_date=upload_date,
                    upload_user = user, upload_photo=upload_photo)
        img_id = img.id
        if img is not None:
            x = Photo.objects.get(id=img_id)
            m = cut_photo(x.upload_photo)
            if m:
                return render(request, 'pages/pages.html')
        #else:
        #    return HttpResponse('false')
    else:
        return HttpResponse('false')

import qiniu
@csrf_exempt
def upload_picVersion2(request):
    ''' upload image '''
    ACCESS_KEY = '92fex8ckMpElKNibqfu1I-fR-R6T3eE4lM3yUw5S'
    SECRET_KEY = 'JW7JnHRqPc_4RbBfVIJot4_2xMsZ4HM--7VzZ3Ps'
    BUCKET_NAME = 'haveatest'
    returnBody = '{\"key\": \"$(key)\",' \
                 '\"bucket\": $(bucket),' \
                 '\"size\": $(fsize),' \
                 '\"w\": $(imageInfo.width),' \
                 '\"h\": $(imageInfo.height),' \
                 '\"uuid\": $(uuid)}'
    PutPolicy = {
        'returnBody':returnBody,
    }
    q = qiniu.Auth(ACCESS_KEY,SECRET_KEY)
    token = q.upload_token(BUCKET_NAME,policy=PutPolicy)

    data = request.FILES['upload_photo']
    description = request.POST['description']
    
    fileKey = FileKey()

    ret, info = qiniu.put_data(token, fileKey, data)
    assert ret['key'] == fileKey

    #dic = json.loads(info.text_body)
    image_url = "http://haveatest.qiniudn.com/" + fileKey 

    user = UserClient.objects.get(user_id = request.user.id)
    ip_addr = request.META['REMOTE_ADDR']

    upload_date = datetime.datetime.now()
    img = Photo.objects.create(description=description, ip_addr=ip_addr, praise=0, upload_date=upload_date,
        upload_user = user, upload_photo=image_url)


    return render(request, 'pages/pages.html')

import random
def FileKey():
    date = datetime.datetime.today()
    random_s = ''
    for i in range(0,16):
        random_s += chr(64+random.randint(1,26))

    return str(date.year) + '/' + str(date.month) + '/' + str(date.day) + '/' + 'huang' + '/' + \
           str(date.hour) + ':' + str(date.minute) + ':' + str(date.second) + '/' + random_s


def cut_photo(url):
    name = str(url).split('/')[4]
    img = Image.open(url)
    name_1 = str(name)
    url_1 = str(url)
    n = name_1.split('.')
    x, y = img.size

    if x < y:
        img1 = img.crop((0,0,x,x))

    else:
        img1 = img.crop((0,0,y,y))

    img2 =  img1.resize((250,250), Image.ANTIALIAS)
    m = n[0] + 'cut' + '.' + n[1]
    u = url_1.split('/')
    ul = u[0] + '/' + u[1] + '/' + u[2] + '/' + u[3] + '/'
    now_root = os.path.join(os.path.dirname(__file__), '..', 'PhotoShare' , 'media' , ul)
    img2.save(now_root + m)
    return True

def get_all_photo(request):
    photoList = Photo.objects.all().order_by('-praise')
    allPhoto = []
    for x in photoList:
        comm = Comment.objects.all().filter(comm_img_id=x.id)

        if comm is not None:
            commnum = len(comm)
        else:
            commnum = 0

        photo = {
            'praise': str(x.praise),
            'upload_photo': x.upload_photo,
            'photo_id': str(x.id),
            'commnum': str(commnum),
        }
        allPhoto = allPhoto + [photo]
    return HttpResponse(json.dumps(allPhoto))


def get_uploadphoto_user_info(request):
    photo_id = request.GET['photo_id']
    photo = Photo.objects.get(id=photo_id)
    user = UserClient.objects.get(id=photo.upload_user_id)
    userinfo = {
        'nickname': user.nickname,
        'signature': user.signature,
        'headshot': user.headshot,
        'description': photo.description,
        'praise': photo.praise,
        'upload_photo': photo.upload_photo,
        'u_id': user.id,
    }
    return HttpResponse(json.dumps(userinfo))

def get_comment_user_info(request):
    photo_id = request.GET['photo_id']
    comment = Comment.objects.all().filter(comm_img_id=photo_id)
    allcomm = []
    if comment is not None:
        for c in comment:
            userinfo = UserClient.objects.get(id=c.comm_user_id)
            if userinfo is not None:
                m = {
                    'content': c.content,
                    'nickname': userinfo.nickname,
                    'headshot': userinfo.headshot,
                }
                allcomm = allcomm + [m]

    return HttpResponse(json.dumps(allcomm))


@csrf_exempt
def user_comment(request):
    if request.method == 'POST':
        form = UserComment(request.POST)
        if form.is_valid():
            user = UserClient.objects.get(user_id=request.user.id)
            comm = Comment.objects.create(content=form.cleaned_data['content'], comm_date=datetime.datetime.now(),
                                          comm_user=user, comm_img=Photo.objects.get(id=form.cleaned_data['comm_img_id']))
            if comm is not None:
                return HttpResponse("ok")
            else:
                return HttpResponse("false")
        else:
            return HttpResponse("false")
    else:
        return HttpResponse("false")


def user_praise(request):
    pid = request.GET['pid']
    photo = Photo.objects.get(id=pid)
    photo.praise = str(int(photo.praise) + 1)
    photo.save()
    return HttpResponse(str(photo.praise))


def user_photo(request):
    user = UserClient.objects.get(user_id=request.user.id)
    photoList = Photo.objects.all().filter(upload_user_id=user.id).order_by('-praise')
    allPhoto = []
    for x in photoList:
        comm = Comment.objects.all().filter(comm_img_id=x.id)
        if comm is not None:
            commnum = len(comm)
        else:
            commnum = 0
        photo = {
            'praise': str(x.praise),
            'upload_photo': x.upload_photo,
            'photo_id': str(x.id),
            'commnum': str(commnum),
        }
        allPhoto = allPhoto + [photo]
    return HttpResponse(json.dumps(allPhoto))


def pages_user_info(request):
    user = UserClient.objects.get(user_id=request.user.id)
    photoList = Photo.objects.all().filter(upload_user_id=user.id)

    praiseNum = 0
    if photoList is not None:
        for x in photoList:
            praiseNum = praiseNum + int(x.praise)

    followedList = Follow.objects.all().filter(followed_user_id=user.id)
    followedNum = 0
    if followedList is not None:
        for x in followedList:
            followedNum = followedNum + 1

    followingList = Follow.objects.all().filter(follow_user_id=user.id)
    followingNum = 0
    if followingList is not None:
        for x in followingList:
            followingNum = followingNum + 1

    m = {
        'nickname': user.nickname,
        'headshot': user.headshot,
        'signature': user.signature,
        'praise_num': str(praiseNum),
        'photo_num': str(len(photoList)),
        'followed_num': str(followedNum),
        'following_num': str(followingNum),
    }

    return HttpResponse(json.dumps(m))

@csrf_exempt
def user_changeinfo(request):
    if request.method == 'POST':
        form = UserChangeInfo(request.POST, request.FILES)
        if form.is_valid():
            user = UserClient.objects.get(user_id=request.user.id)
            user.nickname = form.cleaned_data['nickname']
            user.signature = form.cleaned_data['signature']
            if form.cleaned_data['headshot'] is not None:
                user.headshot = form.cleaned_data['headshot']
            user.save()
            return HttpResponse('success')
    return HttpResponse('error')

@csrf_exempt
def user_changeinfoVersion2(request):
    ''' upload image '''
    ACCESS_KEY = '92fex8ckMpElKNibqfu1I-fR-R6T3eE4lM3yUw5S'
    SECRET_KEY = 'JW7JnHRqPc_4RbBfVIJot4_2xMsZ4HM--7VzZ3Ps'
    BUCKET_NAME = 'haveatest'
    returnBody = '{\"key\": \"$(key)\",' \
                 '\"bucket\": $(bucket),' \
                 '\"size\": $(fsize),' \
                 '\"w\": $(imageInfo.width),' \
                 '\"h\": $(imageInfo.height),' \
                 '\"uuid\": $(uuid)}'
    PutPolicy = {
        'returnBody':returnBody,
    }
    q = qiniu.Auth(ACCESS_KEY,SECRET_KEY)
    token = q.upload_token(BUCKET_NAME,policy=PutPolicy)

    form = UserChangeInfo(request.POST, request.FILES)
    data = request.FILES['headshot']
    user = UserClient.objects.get(user_id=request.user.id)
    user.nickname = request.POST['nickname']
    user.signature = request.POST['signature']
    
    fileKey = FileKey()

    ret, info = qiniu.put_data(token, fileKey, data)
    assert ret['key'] == fileKey

    #dic = json.loads(info.text_body)
    image_url = "http://haveatest.qiniudn.com/" + fileKey 

    user.headshot = image_url

    user.save()

    return HttpResponse("done")

def user_follow(request):
    fd_u_id = request.GET['u_id']
    fg_u_id = request.user.id
    fd_user = UserClient.objects.get(id=fd_u_id)
    fg_user = UserClient.objects.get(user_id=fg_u_id)
    followList = Follow.objects.all().filter(follow_user=fg_user)
    flag = 1
    for x in followList:
        print x
        if fd_user is not x.followed_user:
            flag = 0
    if flag:
        follow = Follow.objects.create(follow_user=fg_user, followed_user=fd_user)
        if follow is not None:
            return HttpResponse('ok')
    return HttpResponse('false')

def following_user_photo(request):
    user = UserClient.objects.get(user_id=request.user.id)
    followingList = Follow.objects.all().filter(follow_user_id=user.id)
    followingPhotoList = []
    for x in followingList:
        userList = UserClient.objects.all().filter(id=x.followed_user_id)
        if userList is not None:
            for y in userList:
                for m in Photo.objects.all().filter(upload_user_id=y.id):
                    pu_info = {
                        'upload_photo': m.upload_photo,
                        'upload_user_id': str(y.id),
                        'photo_id': str(m.id),
                    }
                    followingPhotoList = followingPhotoList + [pu_info]

    return HttpResponse(json.dumps(followingPhotoList))











