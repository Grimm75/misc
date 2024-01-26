ctt - clipboard to text shell helper
====================================
(using xclip and Tesseract)

- Install needed packages (Debian, Ubuntu):

```
sudo apt-get install xclip tesseract-ocr tesseract-ocr-ces tesseract-ocr-rus
```

- Add following line to your ~/.bashrc:

```
alias ctt='xclip -quiet -selection clipboard -t image/png -o 2>/dev/null | tesseract -l ces+eng+rus --psm 11 stdin stdout 2>/dev/null'
```

- Re-source your .bashrc and check new alias presence:
```
. ~/.bashrc
alias ctt
```

- Enjoy.
