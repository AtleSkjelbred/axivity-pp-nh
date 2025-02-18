Install on Windows 10/11:

1: Install Anaconda
2: Install git for Windows (https://gitforwindows.org/)
3: Open anaconda_prompt
4: Clone axivity-pp repository: git clone https://github.com/AtleSkjelbred/axivity-pp-nh.git
5: Navigate to folder: cd axivity-pp-nh
6: Create environment: conda create --name axivity-pp python=3.9 --no-default-packages -y
7: Activate environment: conda activate axivity-pp
8: Install packages: pip install -r requirements.txt

Get started
In terminal, nagivate to the folder: cd axivity-pp-nh
Activate environment: activate axivity-pp
Run the program: python main.py --data-folder <Path to data> (NB: end with /)
Running the program without --data-folder command defaults to folder "data" in axivity-pp-nh