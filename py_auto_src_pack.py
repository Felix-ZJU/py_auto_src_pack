#!python2
# MDK project auto backup.

# usage:
# in MDK, open option for target window
# User tab, After Build/Rebuild group, Run #1 edit, fill in:
# python2 E:\code\py_wheel\py_auto_src_pack.py ..

import re
import os
import sys
import time

def exec_patch(old_path, new_path, patch_file, skip_list):
  str_exclude = ""
  for item in skip_list:
    str_exclude = str_exclude + " -x \"%s\"" % item
  str_patch = "diff -BurN -x prj %s %s %s > %s" % (str_exclude, old_path, new_path, patch_file)
  # print str_patch
  exec_result = os.system(str_patch)
  if exec_result and os.path.exists(patch_file):
    if os.path.getsize(patch_file) > 0:
      # compress
      str_compress = "gzip %s" % patch_file
      exec_result = os.system(str_compress)
    else:
      # delete
      str_clean = "rm %s" % patch_file
      os.system(str_clean)
  return exec_result
# end exec_patch()

def exec_pack(root_path, package_file, skip_list):
  # generate exclude parameter
  str_exclude = ""
  # generate object
  str_object = ""
  for item in os.listdir(root_path):
    if item not in skip_list:
      str_object = str_object + " " + item
  for item in skip_list:
    str_exclude = str_exclude + " --exclude=%s"%item
  str_pack = "tar -cz -C %s %s -f %s %s" % (root_path, str_exclude, package_file, str_object)
  # print str_pack
  exec_result = os.system(str_pack)
  return exec_result
# end exec_pack()

def exec_release(package_file, package_path):
  release_path = package_path + "/last"
  if not os.path.exists(release_path):
    os.mkdir(os.path.realpath(release_path))
  else:
    os.system("rm -r %s/*" % release_path)
  os.system("tar -zxf %s -C %s" % (package_file, release_path))
  return
# end exec_release()

def get_lastbackup_time(package_path, project_name):
  newest_stamp = 0
  newest_item = ""
  for item in os.listdir(package_path):
    m=re.match(r"%s-(\d{8}_\d{6})\.tgz"%project_name, item)
    if(m):
      st = time.mktime(time.strptime(m.group(1), "%Y%m%d_%H%M%S"))
      if st > newest_stamp:
        newest_stamp = st
        newest_item = item
  return [newest_stamp, newest_item]
# end get_lastbackup_time()

def backup(dir_root, package_path, skip_list):
  dir_root = dir_root.strip("\\/")
  package_path = package_path.strip("\\/")
  if not os.path.exists(dir_root):
    return
  if not os.path.exists(package_path):
    os.mkdir(package_path)
  project_version = ""
  if os.path.exists(dir_root+"/version.txt"):
    fp = open(dir_root+"/version.txt", "r")
    project_version = fp.readline()
    print "  project_version:", project_version
    fp.close()
  project_name = os.path.realpath(dir_root).replace('\\','/').split('/')[-1]
  if len(project_version):
    project_name = project_name + "-" + project_version
  [last, last_file] = get_lastbackup_time(package_path, project_name)
  curr = time.time()
  last_date = time.strftime("%Y%m%d", time.localtime(last))
  curr_date = time.strftime("%Y%m%d", time.localtime(curr))

  print "  Last backup: %s," % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(last))

  str_postfix_time = time.strftime("%Y%m%d_%H%M%S", time.localtime())
  if curr_date != last_date or curr-last >= 4*3600:
    # generate package filename
    str_packagename = "%s/%s-%s.tgz"%(package_path, project_name, str_postfix_time)
    print "  Going to create package %s ..." % str_packagename
    exec_pack(dir_root, str_packagename, skip_list)
    exec_release(str_packagename, package_path)
    flag_backup = True
  else:
    str_patchname = "%s/%s-%s.patch"%(package_path, project_name, str_postfix_time)
    print "  Going to create patch %s.gz ..." % str_patchname
    exec_patch(package_path+"/last", dir_root, str_patchname, skip_list)
    flag_backup = False
  return flag_backup
# end backup()

def main(argv):

  argc = len(argv)
  path_root = argv[1] if argc > 1 else "."
  path_pack = argv[2] if argc > 2 else path_root + "/archive"
  file_skip = argv[3] if argc > 3 else path_root + "/.skiplist.txt"

  usr_skip_list = []
  if os.path.exists(file_skip):
    fp = open(file_skip, "r")
    line = fp.readline()
    while line:
      usr_skip_list.append(line.strip("\n\r"))
      line = fp.readline()
    # end while
  # end if
  else:
    '''
    usr_skip_list = [\
    "Objects", \
    "build", \
    "Build", \
    "archive", \
    ".*", \
    "*.bin", \
    "*.o", \
    "*.obj", \
    "*.exe", \
    "*.dll", \
    "*.zip", \
    "*.tar*", \
    "*.tgz", \
    ]
    '''
    pass
  backup(path_root, path_pack, usr_skip_list)
  return 0
# end main()

if __name__ == "__main__":
  sys.exit(main(sys.argv))
# end if
