# Digital Twin Prototype of a PiCar-X
The goal of this project is to give an insight into practice and how the developed of IIoT applications changes.We demonstrate the basic idea of a Digital Twin (Prototype) by the example of a PiCar-X by Sunfounder.
This project was implemented with via ROS packages, which can be connected to a Gazebo simulation.

<img style="display: block; margin: auto;" src="./docs/picarx-gazebo.gif" width="500" />

# Activate GPIO and I2C on Your System
This project based on ROS and Docker. Due to the used interfaces on the RPi, we have to use Linux Kernel functions for GPIO and I2C. Before you can start this project you have to activate GPIO and I2C. If you already activated these modules, you can proceed with ##. Otherwise you have to build these modules first.

- [Install on Ubuntu 20.04](#build-new-linux-kernel)
- [Install on Windows (with WSL2)](#build-new-windows-wsl2-kernel)

<strong>If you are using this project with WSL2, you also have to [install and start the XLaunch](#xlaunch-for-windows). Otherwise you can start Gazebo with Docker.</strong>

If you already have built the modules, you can activate them via 
```console 
    sudo modprobe gpio-mockup gpio_mockup_ranges=1,41
    sudo modprobe i2c-dev
    sudo modprobe i2c-stub chip_addr=0x14
```

# Start with Docker compose
You can start the whole Digital Twin Prototype with the <em>docker-compose</em> file in this folder. We use a core container, where all other containers are built on. When you built the containers the first time, you have to build the core container first.

```console 
    docker compose -f docker-compose-dtp.yml build picarx
```

Afterwards, you can build all containers and start the Digital Twin Prototype when all containers are built.
```console 
    docker compose -f docker-compose-dtp.yml build
    docker compose -f docker-compose-dtp.yml up
```

# Build new Windows WSL2 Kernel
WSL2 Kernel can be found on [the official WSL2 Linux Kernel GitHub page](https://github.com/microsoft/WSL2-Linux-Kernel).

```console
uname -r

# Possible Output: 
5.10.102.1-microsoft-standard-WSL2


sudo apt-install wget unzip build-essential flex bison libssl-dev libelf-dev dwarves

wget https://github.com/microsoft/WSL2-Linux-Kernel/releases/tag/linux-msft-wsl-5.10.102.1.zip
unzip linux-msft-wsl-5.10.102.1.zip

cp ./Microsoft/config-wsl .config

# ALTERNATIVE 1 (activate the modules via GUI):
make menuconfig

# ALTERNATIVE 2 (write the modules to file):
echo CONFIG_GPIOLIB=y >> .config
echo CONFIG_GPIO_SYSFS=y >> .config             
echo CONFIG_GPIO_CDEV=y >> .config
echo CONFIG_GPIO_CDEV_V1=y >> .config
echo CONFIG_GPIO_MOCKUP=m   >> .config           
echo CONFIG_I2C_CHARDEV=m >> .config
echo CONFIG_I2C_STUB=m >> .config


make KCONFIG_CONFIG=.config -j $NumberOfCores    # if you have 4 cores, just type 4 (the more the better)
```

## Activate new WSL2 Kernel:
Create a folder where you will copy the Kernel from the WSL2 VM to Windows, for example C:\WSLKernel. Then
go back to your Linux console and copy the bzImage and shutdown the WSL2 VM:
```console
# IN WSL:
cp arch/x86/boot/bzImage /mnt/c/WSLKernel

# SHUTDOWN WSL2 VIA POWERSHELL
wsl --shutdown
```

Back on Windows you know have to copy the <em>bzImage</em> to the kernel folder <em>C:\Windows\System32\lxss\tools</em>
Then rename the <em>kernel</em> file to <em>kernel.old</em>, <strong>do not delete it</strong>! If something went wrong, you can just restore the old working kernel. 

After you copied the <em>bzImage</em> into the folder, rename <em>bzImage</em> to <em>kernel</em>. Afterwards, start Ubuntu again and go into the WSL2 Kernel folder from the privious steps and install the modules via:

```
make modules_install
```

If you built and installed the new kernel properly, you should now be able to [activate GPIO and I2C](#activate-gpio-and-i2c-on-your-system). 

## Build new Linux-Kernel
Download your prefered Kernel version:

First check your Kernel version on your system:

```console
uname -r

# POSSIBLE RESULT:
On Ubuntu 20.04: 5.13.0-48-generic
```

Install all the modules required for the Kernel's building

```
sudo apt-install wget unzip build-essential flex bison libssl-dev libelf-dev dwarves ncurses-dev zstd
```

### Build with Linux
```console
uname -r

# POSSIBLE RESULT:
On Ubuntu 20.04: 5.13.0-48-generic

sudo apt-install wget unzip build-essential flex bison libssl-dev libelf-dev dwarves ncurses-dev zstd

wget https://mirrors.edge.kernel.org/pub/linux/kernel/v5.x/linux-5.13.tar.gz

tar xf linux-5.13.tar.gz

cd linux-5.13/

make clean && make mrproper

cp /usr/lib/modules/$(uname -r)/build/.config ./

# ALTERNATIVE 1 (activate the modules via GUI):
make menuconfig

# ALTERNATIVE 2 (write the modules to file):
echo CONFIG_GPIOLIB=y >> .config
echo CONFIG_GPIO_SYSFS=y >> .config             
echo CONFIG_GPIO_CDEV=y >> .config
echo CONFIG_GPIO_CDEV_V1=y >> .config
echo CONFIG_GPIO_MOCKUP=m   >> .config           
echo CONFIG_I2C_CHARDEV=m >> .config
echo CONFIG_I2C_STUB=m >> .config

make scripts

# Disable the key options, otherwise the kernel may wont be built properly
scripts/config --disable CONFIG_SYSTEM_REVOCATION_KEYS
scripts/config --disable CONFIG_SYSTEM_TRUSTED_KEYS


# This will take quite some time, with more cores you are faster
make -j #NumberOfCores
make bzImage
make modules_install
make install

sudo update-grub

sudo reboot
```

After reboot you can check if your new kernel is activated by:

```consle
uname -r

# Result should be the Kernel version you wanted to install, e.g.:
linux-5.13
```

If you built and installed the new kernel properly, you should now be able to [activate GPIO and I2C](#activate-gpio-and-i2c-on-your-system). 

## XLaunch for Windows
[Download the VcXsrv X Server for Windows](https://sourceforge.net/projects/vcxsrv/).
Start the application with following configuration:

1. First Screen: Multiple Windows
2. Second Screen: Start no client
3. Third Screen: Deactivate "<em>Native opengl</em>"
4. Fourth Screen: Start