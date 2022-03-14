#!/bin/bash
# Install fonts to build PDF


###########################################################
# Make sure system font dir exists already, if not, run:
# sudo mkdir /usr/share/fonts/opentype/

# Make sure unzip is installed already, if not, run:
# sudo apt-get install unzip

# fc-cache is required, if not already installed, run:
# sudo apt install fontconfig
###########################################################


# En

wget -O source-serif-pro.zip https://www.fontsquirrel.com/fonts/download/source-serif-pro
unzip source-serif-pro -d source-serif-pro
sudo mv source-serif-pro /usr/share/fonts/opentype/

wget -O source-sans-pro.zip https://www.fontsquirrel.com/fonts/download/source-sans-pro
unzip source-sans-pro -d source-sans-pro
sudo mv source-sans-pro /usr/share/fonts/opentype/

wget -O source-code-pro.zip https://www.fontsquirrel.com/fonts/download/source-code-pro
unzip source-code-pro -d source-code-pro
sudo mv source-code-pro /usr/share/fonts/opentype/

wget -O Inconsolata.zip https://www.fontsquirrel.com/fonts/download/Inconsolata
unzip Inconsolata -d Inconsolata
sudo mv Inconsolata /usr/share/fonts/opentype/

sudo fc-cache -f -v

# Zh
wget https://github.com/adobe-fonts/source-han-sans/releases/download/2.004R/SourceHanSansSC.zip
wget -O SourceHanSerifSC.zip https://github.com/adobe-fonts/source-han-serif/releases/download/2.001R/09_SourceHanSerifSC.zip

unzip SourceHanSansSC.zip -d SourceHanSansSC
unzip SourceHanSerifSC.zip -d SourceHanSerifSC

sudo mv SourceHanSansSC SourceHanSerifSC /usr/share/fonts/opentype/
sudo fc-cache -f -v

# KO

wget https://github.com/adobe-fonts/source-han-sans/releases/download/2.004R/SourceHanSansK.zip
wget -O SourceHanSerifK.zip https://github.com/adobe-fonts/source-han-serif/releases/download/2.001R/08_SourceHanSerifK.zip

unzip SourceHanSansK.zip -d SourceHanSansK
unzip SourceHanSerifK.zip -d SourceHanSerifK

sudo mv SourceHanSansK SourceHanSerifK /usr/share/fonts/opentype/
sudo fc-cache -f -v

# JA

wget https://github.com/adobe-fonts/source-han-sans/releases/download/2.004R/SourceHanSansJ.zip
wget -O SourceHanSerifJ.zip https://github.com/adobe-fonts/source-han-serif/releases/download/2.001R/07_SourceHanSerifJ.zip

unzip SourceHanSansJ.zip -d SourceHanSansJ
unzip SourceHanSerifJ.zip -d SourceHanSerifJ

sudo mv SourceHanSansJ SourceHanSerifJ /usr/share/fonts/opentype/
sudo fc-cache -f -v


# Remove all zip files
rm Source*.zip source*.zip Inconsolata.zip
