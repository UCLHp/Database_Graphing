

location = '\\\\mpb-dc101\\rtp-share$\\protons\\Work in Progress\\Christian\\Database\\Photon\\sample.txt'

text_file = open(location, 'w')
n = text_file.write('Hello World 2')
text_file.close()
