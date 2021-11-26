Title: Screen Reader for the Visually Impaired

Description of Project:

This is a project for the visually impaired in which it helps them navigate webpages by reading out what's on the
webpage using OCR and text-to-speech. As this project focuses on enhancing the experience for visually impaired
users it relies on the use of the keyboard for the user interaction with the computer and sound for the computer
interaction with the user.

Instructions to Run Project:

1. Go to any webpage on Google Chrome (https://en.wikipedia.org/wiki/Pet)
2. Run the program; it will tell you to press space bar
3. The program will read some instructions that include pressing 'l' to leave the instructions sections, pressing
'd' to change the accent, pressing 'a' to change the ocr to arabic application, etc.

    Note: The language in which the application will run is in the language of the last spoken language
    (English or Arabic)

4. After you exit from the instruction section, go to the webpage you want to be read and press Alt. 
5. You can use the screen reader now. Hover with your mouse a section you want to be read and press X (only do this
after the program tells you too)
6. You can translate sections of the webpage using T, the program will provide you with further instructions.
7. To leave the program press Escape


Bug to Watch Out For: The TTS doesn't stop when a new TTS is activated, therefore, before clicking anywhere new or pressing
a new button, wait for the TTS to stop speaking.

How to install any needed libraries:

    Note: I also used the OS module, but that was preinstalled into my IDE

	1. PyAutoGui

        Install PyAutoGui through pip - for more information on installation: https://pyautogui.readthedocs.io/en/latest/install.html
        Give your editor/IDE permission to computer accessibility
        You can check if it works by running a basic PyAutoGui program that takes a screenshot of your screen, however, try testing it by changing to your internet browser as soon as you click run on the program.

	2. Pynput

        Install Pynput through pip - for more information on installation: https://pypi.org/project/pynput/

	3. OpenCV

        Install OpenCV through pip - for more information on installation: https://pypi.org/project/opencv-python/

	4. Google Text to Speech

        Install gTTS through pip - for more information on installation: https://pypi.org/project/gTTS/

	5. PlaySound (May cause issues if not run on Python 3.7)

        Install PlaySound through pip - for more information on installation: https://pypi.org/project/playsound/

	6. PyTesseract

        Install homebrew (or anaconda - however I am not sure how to install tesseract through anaconda)
        Install tesseract through homebrew (or anaconda) - ensure that it’s installed in the same path that you are running the tech demo file
        For homebrew: "brew install tesseract" and "brew install tesseract-lang"
        Install pytesseract through pip
        For More Information: https://pypi.org/project/pytesseract/

    7. Image AI
        For Image AI you need:

            Tensorflow : !pip3 install tensorflow
            OpenCV : !pip3 install opencv-python
            Keras : !pip3 install keras
            ImageAI : !pip3 install imageai — upgrade

        Download predefined model from here -
        https://drive.google.com/file/d/1avRKkoF7PagdPYdgZr_fG3DhFYt_JEXv/view?usp=sharing

        For More Information =
        https://medium.datadriveninvestor.com/ai-object-detection-using-only-10-lines-of-code-imageai-89d3ba9886ea

    8. Google Translation API

        pip3 install googletrans

        If this error arises (AttributeError: 'NoneType' object has no attribute 'group')
            pip3 uninstall googletrans
            pip3 install googletrans==3.1.0a0

        For More Information =
        https://www.thepythoncode.com/article/translate-text-in-python

Shortcut Commands:
During the instruction stage after program says "Press spacebar...":
    1. Press L to skip instructions and directly use the screen reader
    2. Press A to directly go to the arabic instructions