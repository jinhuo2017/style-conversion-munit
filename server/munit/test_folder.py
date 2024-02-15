"""
Copyright (C) 2018 NVIDIA Corporation.  All rights reserved.
Licensed under the CC BY-NC-SA 4.0 license (https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode).
"""
from __future__ import print_function
from utils import get_config, pytorch03_to_pytorch04
from trainer import MUNIT_Trainer, UNIT_Trainer
import argparse
from torch.autograd import Variable
import torchvision.utils as vutils
import sys
import torch
import os
from torchvision import transforms
from PIL import Image
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument('--config', type=str, default='configs/day2night_folder.yaml', help="net configuration")
parser.add_argument('--input_folder', type=str, default='/data/gezi/cyc_img/', help="input image path")
parser.add_argument('--output_folder', type=str, default='fcn/cyc/real', help="output image path")
parser.add_argument('--checkpoint', type=str, default='outputs/day2night_folder/checkpoints/gen_00026950.pt', help="checkpoint of autoencoders")
parser.add_argument('--style', type=str, default='', help="style image path")
parser.add_argument('--a2b', type=int, default=1, help="1 for a2b and others for b2a")
parser.add_argument('--seed', type=int, default=10, help="random seed")
parser.add_argument('--num_style',type=int, default=1, help="number of styles to sample")
parser.add_argument('--synchronized', action='store_true', help="whether use synchronized style code or not")
parser.add_argument('--output_only', action='store_true', help="whether use synchronized style code or not")
parser.add_argument('--output_path', type=str, default='.', help="path for logs, checkpoints, and VGG model weight")
parser.add_argument('--trainer', type=str, default='MUNIT', help="MUNIT|UNIT")
opts = parser.parse_args()

#epoch = 24

#opts.input_folder = '/data/gezi/cyc_img'
opts.input_folder = '/home/lyc/data/ll/yolo/data/custom/train_images/'
#opts.input_folder = '/home/lyc/data/ll/dataset/BDD_sunny2rainy/test/A/'

opts.output_folder = '/home/lyc/data/ll/yolo/data/custom/munit_fake/'
# opts.checkpoint = 'outputs/syn2city_folder/checkpoints/gen_00{:06d}.pt'.format((epoch+1)*1060)
#opts.checkpoint = 'outputs/bdd_sunny2rainy/checkpoints/gen_00024128.pt'

torch.manual_seed(opts.seed)
torch.cuda.manual_seed(opts.seed)
if not os.path.exists(opts.output_folder):
    os.makedirs(opts.output_folder)

# Load experiment setting
config = get_config(opts.config)
opts.num_style = 10 if opts.style != '' else opts.num_style

# Setup model and data loader
config['vgg_model_path'] = opts.output_path
if opts.trainer == 'MUNIT':
    style_dim = config['gen']['style_dim']
    trainer = MUNIT_Trainer(config)
elif opts.trainer == 'UNIT':
    trainer = UNIT_Trainer(config)
else:
    sys.exit("Only support MUNIT|UNIT")

try:
    state_dict = torch.load(opts.checkpoint)
    trainer.gen_a.load_state_dict(state_dict['a'])
    trainer.gen_b.load_state_dict(state_dict['b'])
except:
    state_dict = pytorch03_to_pytorch04(torch.load(opts.checkpoint), opts.trainer)
    trainer.gen_a.load_state_dict(state_dict['a'])
    trainer.gen_b.load_state_dict(state_dict['b'])

trainer.cuda()
trainer.eval()
encode = trainer.gen_a.encode if opts.a2b else trainer.gen_b.encode # encode function
style_encode = trainer.gen_b.encode if opts.a2b else trainer.gen_a.encode # encode function
decode = trainer.gen_b.decode if opts.a2b else trainer.gen_a.decode # decode function

if 'new_size' in config:
    new_size = config['new_size']
else:
    if opts.a2b==1:
        new_size = config['new_size_a']
    else:
        new_size = config['new_size_b']
new_size=(608,1024)
with torch.no_grad():
    transform = transforms.Compose([#transforms.Resize(new_size),
                                    transforms.ToTensor(),
                                    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
    imgs = os.listdir(opts.input_folder)
    for i, img in tqdm(enumerate(imgs)):
        name = img.split('.')[0]
        img_path = os.path.join(opts.input_folder, img)
        image = Variable(transform(Image.open(img_path).convert('RGB')).unsqueeze(0).cuda())
        style_image = Variable(transform(Image.open(opts.style).convert('RGB')).unsqueeze(0).cuda()) if opts.style != '' else None

        # Start testing
        content, _ = encode(image)

        if opts.trainer == 'MUNIT':
            style_rand = Variable(torch.randn(opts.num_style, style_dim, 1, 1).cuda())
            if opts.style != '':
                _, style = style_encode(style_image)
            else:
                style = style_rand
            for j in range(opts.num_style):
                s = style[j].unsqueeze(0)
                outputs = decode(content, s)
                outputs = (outputs + 1) / 2.
                #path = os.path.join(opts.output_folder,  name+'.png')
                path = os.path.join(opts.output_folder, name+'.jpg')
                vutils.save_image(outputs.data, path, padding=0, normalize=True)
                #vutils.save_image(image.data, os.path.join(opts.output_folder,  name+'_real.png'), padding=0, normalize=True)

        else:
            pass

        if  opts.output_only:
        # also save input images
            vutils.save_image(image.data, os.path.join(opts.output_folder,  name+'_real.png'), padding=0, normalize=True)

