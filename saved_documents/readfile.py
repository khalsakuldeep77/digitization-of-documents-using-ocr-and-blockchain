f = open("testocr.png.txt", "r")
new =f.readlines()
x=[]
for i in range(len(new)):
    x.append(new[i].rstrip('\n'))
new_string=''.join(x)
print(new_string)
file1 = open("testocr_new.txt","a")
file1.write(new_string)
file1.close()


