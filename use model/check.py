import torch
print(torch.cuda.is_available())  # должно быть True
print(torch.cuda.get_device_name(0))  # твоя RTX 2060
