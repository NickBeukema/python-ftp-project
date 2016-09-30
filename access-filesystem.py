import os
import pdb


currdir=os.path.abspath('.')


# LIST
def parseFileList(fileList):
  fileList.sort()
  return "\n".join(fileList)

files_in_dir = os.listdir(currdir)
file_string = parseFileList(files_in_dir);


# RETR
the_file = open(files_in_dir[1], 'rb')
data = the_file.read(1024)
file_contents = data

while data:
  data = the_file.read(1024)
  # Send data over connection
  file_contents += data


# Or supposedly you can just send it all at once
#
# socket.send(the_file.read())


# STOR
filename = "file.txt"
filepath = os.path.join(filename)

# Open the file and recieve the contents
# to save in it
#
# fi = open(filepath, "wb")
# data = socket.recv()
# fi.write(data)


pdb.set_trace()
