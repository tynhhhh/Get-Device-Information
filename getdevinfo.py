import platform
import wmi
import hashlib
from math import ceil
from GPUtil import getGPUs
from socket import gethostbyname
import json

def get_sys_info():
    c = wmi.WMI()
    platf = platform.system().lower()
    hostname = ''
    OSArchitecture = ''
    ver = ''
    CurrentTimeZone = ''
    CountryCode = ''
    for title in c.Win32_OperatingSystem():
        hostname += str(title.CSName)
        ver += str(title.Caption)
        OSArchitecture += str(title.OSArchitecture)
        CurrentTimeZone += str(title.CurrentTimeZone)
        CountryCode += str(title.CountryCode)

    ip_address = gethostbyname(hostname)
    return {
        'Host name': hostname,
        'Platform': platf,
        'Version': ver,
        'OS Architecture': OSArchitecture,
        'Country Code': CountryCode,
        'Current Time Zone': CurrentTimeZone,
        'IP Address': ip_address
    }
    
def get_cpu_hwid():
    c = wmi.WMI()
    processors = c.Win32_Processor()
    cpu_name = ""
    cpu_hwid = ""
    for processor in processors:
        cpu_hwid += processor.ProcessorId.strip()
        cpu_name += processor.Name
    return cpu_hwid, cpu_name


def get_total_cpu_cores():
    c = wmi.WMI()
    processors = c.Win32_Processor()
    total_cpu_cores = 0
    for processor in processors:
        total_cpu_cores += processor.NumberOfCores
    return total_cpu_cores


def get_motherboard_hwid():
    c = wmi.WMI()
    motherboards = c.Win32_BaseBoard()
    return motherboards[0].SerialNumber.strip()


def get_graphics_card_model():
    c = wmi.WMI()
    graphics_cards = c.Win32_VideoController()
    if graphics_cards:
        graphics_card = graphics_cards[0]
        return graphics_card.Name.strip()
    return None


def get_bios_hwid():
    c = wmi.WMI()
    bios = c.Win32_BIOS()[0]
    return bios.SerialNumber


def get_windows_uuid():
    c = wmi.WMI()
    os = c.Win32_OperatingSystem()[0]
    return os.SerialNumber


def get_total_ram():
    c = wmi.WMI()
    ram_modules = c.Win32_PhysicalMemory()
    total_ram = 0
    for module in ram_modules:
        total_ram += int(module.Capacity)
    return str(ceil(total_ram / (1024**3))) + 'Gb'


def check_for_all_existing_users():
    c = wmi.WMI()
    users = c.Win32_UserAccount()
    user_names = []
    for user in users:
        user_names.append(user.Name)
    return user_names


def get_mac_addresses():
    c = wmi.WMI()
    mac_addresses = []
    for interface in c.Win32_NetworkAdapterConfiguration(IPEnabled=1):
        mac_addresses.append(interface.MACAddress)
    return mac_addresses


def get_ram_speed():
    c = wmi.WMI()
    ram_modules = c.Win32_PhysicalMemory()
    ram_speed = 0
    for module in ram_modules:
        ram_speed = module.Speed
    return ram_speed


def get_cpu_vendor():
    c = wmi.WMI()
    processors = c.Win32_Processor()
    processor_vendor = ""
    for processor in processors:
        processor_vendor += processor.Manufacturer.strip()
    return processor_vendor


def get_disks_model():
    c = wmi.WMI()
    disks = c.Win32_DiskDrive()
    disks_names = ""

    for ssd in disks:
        interface_types = ssd.InterfaceType.split()

        if any(interface_type.lower() in ['scsi', 'ide', 'sata', 'nvme'] for interface_type in interface_types):
            disks_names += ssd.Model.strip()

    return disks_names


def get_disks_hwid():
    c = wmi.WMI()
    disks = c.Win32_DiskDrive()

    disks_hwids = []

    for disk in disks:
        interface_types = disk.InterfaceType.split()

        if any(interface_type.lower() in ['scsi', 'ide', 'sata', 'nvme'] for interface_type in interface_types):
            ssd_hardware_id = disk.SerialNumber.strip()
            disks_hwids.append(ssd_hardware_id)

    return disks_hwids


def get_graphics_card_vram():
    gpus = getGPUs()
    max_vram = 0
    for gpu in gpus:
        vram = gpu.memoryTotal
        if vram > max_vram:
            max_vram = vram

    if max_vram < 1024:
        return str(int(max_vram)) + 'Mb'
    
    return str(int(max_vram /1024)) + 'Gb'


def get_graphics_card_uuid():
    c = wmi.WMI()
    graphics_cards = c.Win32_VideoController()
    if graphics_cards:
        graphics_card = graphics_cards[0]
        return graphics_card.PNPDeviceID
    return None


def get_device_infomation():
    system = get_sys_info()
    cpu_id, cpu_name = get_cpu_hwid()
    cpu_vendor = get_cpu_vendor()
    cpu_scores = get_total_cpu_cores()
    ram = get_total_ram()
    ram_speed = get_ram_speed()
    disk_model = get_disks_model()
    disk_hwid = get_disks_hwid()
    gpu = get_graphics_card_model()
    gpu_vram = get_graphics_card_vram()
    gpu_uuid = get_graphics_card_uuid()
    bios = get_bios_hwid()
    motherboard_hwid = get_motherboard_hwid()
    windows_uuid = get_windows_uuid()
    mac_address = get_mac_addresses()
    hostname = get_sys_info()['Host name']

    hwid = ""
    hwid += str(hostname)
    hwid += str(disk_model)
    hwid += str(disk_hwid)
    hwid += str(cpu_vendor)
    hwid += str(cpu_id)
    hwid += str(cpu_scores)
    hwid += str(ram)
    hwid += str(ram_speed)
    hwid += str(gpu)
    hwid += str(gpu_vram)
    hwid += str(gpu_uuid)
    hwid += str(bios)
    hwid += str(motherboard_hwid)
    hwid += str(windows_uuid)
    hwid += str(mac_address)

    hwid = hashlib.sha256(hwid.encode()).hexdigest()


    hwid = hwid.upper()
    hwid = '-'.join(hwid[i:i + 8] for i in range(0, len(hwid), 8))
    return {
        'System': system,
        'CPU': {
            'ID': cpu_id,
            'Name': cpu_name,
            'Vendor': cpu_vendor,
            'Scores': cpu_scores
        },
        'Ram': {
            'Total': ram,
            'Speed': ram_speed
        },
        'GPU': {
            'ID': gpu_uuid,
            'Name': gpu,
            'Vram': gpu_vram
        },
        'Disk': {
            'ID': disk_hwid,
            'Model': disk_model
        },
        'Bios': bios,
        'Motherboard': motherboard_hwid,
        'Mac address': mac_address,
        'Unique ID': hwid
    }

def main():
    device_info = get_device_infomation()
    print(device_info)
    with open('systeminformation.mmologin', 'w') as file:
        file.write(json.dumps(get_device_infomation()))
        file.close()
if __name__ =="__main__":
    main()
    input("Press Enter to exit...")