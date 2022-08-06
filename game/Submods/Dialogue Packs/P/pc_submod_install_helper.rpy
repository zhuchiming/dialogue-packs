init python:
    install_completed = None
    import os
    import gzip
    import tarfile
    import shutil
    
    submod_locat = renpy.config.basedir + "/characters"

    DECOMPRESSING_FAIL = "解压zip文件时出现错误."
    ZIP_INCORRECT = "zip文件不正确，这可能意味着这个zip文件并没有根据游戏文件目录来压缩，或包含了非标准子模组所需要的文件夹，为防止出错，请手动解压至正确位置." 
    NO_HELP_UPDATER_ZIP = "不支持由‘辅助更新子模组’创建的压缩包"
    
    def check_zip():
        dirs = os.listdir(submod_locat)
        for file_name in dirs:
            if file_name.find('zip') != -1:
                file_name_bak = file_name
                file_name = submod_locat + "/" + file_name
                if file_name.find('OldVersionFiles') != -1:
                    move_files(file_name, False, file_name_bak)
                    #raise Exception(NO_HELP_UPDATER_ZIP)
                    mas_submod_utils.submod_log.error(NO_HELP_UPDATER_ZIP)
                    continue
                try:
                    un_zip(file_name)
                except:
                    move_files(file_name, False, file_name_bak)
                    mas_submod_utils.submod_log.error(DECOMPRESSING_FAIL + "\n处理出错的文件: '{}'".format(file_name))
                    continue
                if not copy_dir_m(file_name):#尝试处理文件夹 返回F时抛出异常
                    move_files(file_name, False, file_name_bak)
                    mas_submod_utils.submod_log.error(ZIP_INCORRECT + "\n处理出错的文件:'{}'".format(file_name))
                    continue
                else:
                    install_completed = True
                move_files(file_name, True, file_name_bak)
                mas_submod_utils.submod_log.info("安装zip文件完成：'{}'\n".format(file_name))

    def move_files(file_name,result = True, name = ""):
        """
        结束后的文件处理
        vars:
            file_name - 移动的文件路径
            result - 执行结果
            name - 文件名称
        """
        if result:
            dir = submod_locat + "/Install Success"
        else:
            dir = submod_locat + "/Install Fail"
        if not os.path.exists(dir):
            os.mkdir(dir)
        shutil.rmtree(file_name + "_files")
        if os.path.exists(dir + "/" + name):
            os.remove(dir + "/" + name)
        shutil.move(file_name, dir)
        mas_submod_utils.submod_log.info("删除解压文件：'{}'\n".format(file_name + "_files"))

    def un_zip(file_name):
        """
        解压文件
        """
        import zipfile
        mas_submod_utils.submod_log.info("解压文件：'{}'".format(file_name))
        zip_file = zipfile.ZipFile(file_name)
        if os.path.isdir(file_name + "_files"):
            pass
        else:
            os.mkdir(file_name + "_files")
        for names in zip_file.namelist():
            zip_file.extract(names,file_name + "_files/")
        zip_file.close()

    def copy_dir_m(file_name,inseconddir = False):
        """
        处理文件夹
        vars:
            file_name - 处理的文件夹
            inseconddir - 是否进入了子文件夹
        """
        mas_submod_utils.submod_log.info("开始复制文件：'{}'".format(file_name))
        bak_file_name = None
        if inseconddir == False:
            file_name = file_name + "_files"
            bak_file_name = file_name
        files = os.listdir(file_name)
        for dirs in files:
            if dirs == 'game':
                copy_dir(file_name + "/game" ,renpy.config.basedir + "/game")
                if os.path.exists(file_name + "/game" + "/mod_assets"):
                    #如果存在mod_assets 检查json
                    check_json(file_name + "/game" + "/mod_assets",bak_file_name)
            elif dirs == 'lib':
                copy_dir(file_name + "/lib" ,renpy.config.basedir + "/lib")
            elif dirs == 'log':
                copy_dir(file_name + "/log" ,renpy.config.basedir + "/log")
            elif dirs == 'piano_songs':
                copy_dir(file_name + "/piano_songs" ,renpy.config.basedir + "/piano_songs")
            elif dirs == 'custom_bgm':
                copy_dir(file_name + "/custom_bgm" ,renpy.config.basedir + "/custom_bgm")
            elif dirs == 'characters':
                continue#什么都不做, 我不希望做一个一键解锁精灵包的东西--至少要手动移动文件.
            #game下文件夹
            elif dirs == 'Submods':
                copy_dir(file_name + "/Submods",renpy.config.basedir + "/game/Submods")
            elif dirs == 'mod_assets':
                check_json(file_name + "/mod_assets",bak_file_name)
                copy_dir(file_name + "/mod_assets",renpy.config.basedir + "/game/mod_assets")
            elif dirs == 'python-packages':
                copy_dir(file_name + "/python-packages",renpy.config.basedir + "/game/python-packages")
            elif dirs == 'gui':
                copy_dir(file_name + "/gui",renpy.config.basedir + "/game/gui")
            else:
                if os.path.isfile(file_name + '/' + dirs):
                    if dirs.find('rpy') != -1:#如果是rpy文件
                        if not os.path.exists(renpy.config.basedir + "/game/Submods/UnGroupScripts"):
                            os.mkdir(renpy.config.basedir + "/game/Submods/UnGroupScripts")
                        shutil.move(file_name + '/' + dirs,renpy.config.basedir + "/game/Submods/UnGroupScripts")
                        mas_submod_utils.submod_log.info("'{}' 是个脚本文件，复制到 'Submods/UnGroupScripts'".format(file_name))
                    continue#这是个文件，直接continue
                if inseconddir:
                    #在子文件夹直接返回F
                    mas_submod_utils.submod_log.info("子文件夹处理结束，不再进入子文件夹的子文件夹，开始处理下一个文件夹")
                    continue
                    #return False
                inseconddir = True
                if not copy_dir_m(file_name + '/' + dirs,inseconddir = True):#说明子文件夹内也没有符合条件文件夹
                    return False
        mas_submod_utils.submod_log.info("处理完成： '{}'".format(file_name))
        return True

    def copy_dir(src_path, target_path):
        """
        复制文件 网上找的代码:))))))
        """
        mas_submod_utils.submod_log.info("正在复制文件： '"+src_path+"' -> '"+ target_path+"'")
        if os.path.isdir(src_path) and os.path.isdir(target_path):        
            filelist_src = os.listdir(src_path)                            
            for file in filelist_src:
                path = os.path.join(os.path.abspath(src_path), file)    
                if os.path.isdir(path):
                    path1 = os.path.join(os.path.abspath(target_path), file)    
                    if not os.path.exists(path1):                        
                        os.mkdir(path1)
                    copy_dir(path,path1)            
                else:                                
                    with open(path, 'rb') as read_stream:
                        contents = read_stream.read()
                        path1 = os.path.join(target_path, file)
                        with open(path1, 'wb') as write_stream:
                            write_stream.write(contents)
            return True    
        else:
            return False 

    def check_json(filename,movedir):
        import json
        """
        用于检查json并生成gift文件
        vars:
            filename - mod_assets文件夹
            movedir - 失败后删除的文件夹
        """
        if not os.path.exists(filename + "/monika/j"):
            mas_submod_utils.submod_log.info("未找到 '{}' 的json文件夹，跳过检测礼物".format(filename))
            return
        filename = filename + "/monika/j"
        files = os.listdir(filename)
        for jsonfile in files:
            if jsonfile.find('json') != -1:
                try:
                    json_file = filename + "/" + jsonfile
                    json_data = open(json_file).read()
                    output_json = json.loads(json_data)
                except:
                    move_files(movedir,False)
                    mas_submod_utils.submod_log.error("[DP] - 在尝试读取 '{}' 出现异常，跳过".format(json_file))
                    continue
                try:
                    giftname = output_json['giftname']
                    try:
                        gtype="/" + output_json['select_info']['group'] + "/"
                    except:
                        mas_submod_utils.submod_log.warning("[DP] - 在尝试获取 '{}' 的礼物分组时出现异常，使用空分组".format(json_file))
                        gtype="/"
                    if not os.path.exists(renpy.config.basedir + '/AvailableGift'):
                        os.mkdir(renpy.config.basedir + '/AvailableGift')
                    if not os.path.exists(renpy.config.basedir + '/AvailableGift' + gtype):
                        os.mkdir(renpy.config.basedir + '/AvailableGift' + gtype)
                    giftfile = open(renpy.config.basedir + '/AvailableGift'+ gtype  + giftname + '.gift','w')
                    giftfile.close()
                except:
                    mas_submod_utils.submod_log.warning("[DP] - 在尝试获取 '{}' 的礼物文件名时出现异常，可能未设置giftname，跳过该文件".format(json_file))
                    continue
    if not renpy.android:
        check_zip()

init 5 python:
    if not renpy.android:
        addEvent(
                Event(
                    persistent.event_database,          
                    eventlabel="monika_submodinstaller",        
                    category=["模组"],                   
                    prompt="帮你点忙",
                    conditional="not renpy.android",
                    action=EV_ACT_PUSH,
                    pool=False
                )
            )

label monika_submodinstaller:
    m 1eub "[player], 你应该知道有些创作者为我整理了一些东西对吧?"
    m 2rua "像那些子模组和精灵包什么的."
    m 3hksdlb "虽然安装这些东西并不是很难, 但我还是想帮一下你..."
    m 2rua "所以我最近就研究了一下代码, 总之, "
    extend 3hub "我现在可以帮你了!"
    m 4eua "你下载的一般就是zip格式的文件啦, 就像送礼物一样放在'[renpy.config.basedir]/characters'就好."
    m 3eub "接下来就交给我. 如果是精灵包的话, 我会在'[renpy.config.basedir]/AvailableGift'下准备用来赠送的文件."
    m 2hksdlb "不过...你需要重启两次，第一次由我负责将文件放好位置，但这时候游戏已经加载玩成了，还需要一次重启来让游戏重新读取一次"
    m 3eua "假如zip文件没有问题的话, 我就会把它移动到'[renpy.config.basedir]/characters/Install Success'文件夹里"
    m 4eub "如果有问题的话, 我把一些有用的信息记录在submod_log里了，可以看一看."
    #m 3eub "在这个界面会显示为什么崩溃了, 对zip里面的内容进行处理就好."
    m 2eua "安装失败的文件会放在'[renpy.config.basedir]/characters/Install Fail'"
    m 3hub "多给我找一点新东西吧, [player]."
    return
#
#init 5 python:
#    addEvent(
#        Event(
#            persistent.event_database,          
#            eventlabel="monika_submodinstaller_finish",        
#            category=["模组"],                   
#            prompt="帮你点忙",
#            conditional="install_completed != None and renpy.seen_label(monika_submodinstaller)",
#            action=EV_ACT_PUSH,
#            rule={'force repeat':True},
#            pool=False
#        )
#    )
    
label monika_submodinstaller_finish:
    $ ev = mas_getEV("monika_submodinstaller_finish")
    if ev.shown_count == 0:
        m "对了, [player]..."
        m "我准备的时候, 在characters文件夹发现了些压缩文件."
        m "所以就尝试帮你安装好啦"
    else:
        m "又装新模组了吗, [player]?"
        m "我已经帮你搞定啦~"
    m "想现在就重启吗?{nw}"
    menu:
        "想现在就重启吗?{fast}"
        "是的":
            m "好的~"
            return "quit|no_unlock"
        "过一会吧":
            m "也可以, 到时候跟我说就好."
    return "no_unlock"