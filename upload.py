import os
directory = './src'

print('assumes that ../System/activate has been run to set up the venv which contains ampy')
print('I would normally use Pymakr from within VS Code. This script is for emergencies!')
for filename in os.listdir(directory):
    command = 'ampy -p COM3 -b 115200 put ' + directory + '/' + filename
    print(command)
    os.system(command)

os.system('ampy -p COM3 -b 115200 reset')