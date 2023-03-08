import logging
import pathlib
import os

import pytest
from pytest_lazyfixture import lazy_fixture
import pyvista as pv
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import cv2
from scipy.spatial.transform import Rotation as R
from pytest_lazyfixture  import lazy_fixture
import skimage.transform
import torch
import torchvision
import vision6D as vis

import logging
import PIL

logger = logging.getLogger("vision6D")
np.set_printoptions(suppress=True)

# size: (1920, 1080)
@pytest.fixture
def app():
    return vis.App(register=True, scale=1)
    
def test_load_image(app):
    image_source = np.array(Image.open(vis.config.IMAGE_PATH_5997))
    app.set_image_opacity(1)
    app.load_image(image_source, scale_factor=[0.01, 0.01, 1])
    app.set_reference("image")
    app.plot()

@pytest.mark.parametrize(
    "image_path, ossicles_path, facial_nerve_path, chorda_path, gt_pose",
    [# right ossicles
    (vis.config.IMAGE_PATH_455, vis.config.OSSICLES_MESH_PATH_455_right, vis.config.FACIAL_NERVE_MESH_PATH_455_right, vis.config.CHORDA_MESH_PATH_455_right, vis.config.gt_pose_455_right),
    (vis.config.IMAGE_PATH_5997, vis.config.OSSICLES_MESH_PATH_5997_right, vis.config.FACIAL_NERVE_MESH_PATH_5997_right, vis.config.CHORDA_MESH_PATH_5997_right, vis.config.gt_pose_5997_right),
    (vis.config.IMAGE_PATH_6088, vis.config.OSSICLES_MESH_PATH_6088_right, vis.config.FACIAL_NERVE_MESH_PATH_6088_right, vis.config.CHORDA_MESH_PATH_6088_right, vis.config.gt_pose_6088_right),
    (vis.config.IMAGE_PATH_6108, vis.config.OSSICLES_MESH_PATH_6108_right, vis.config.FACIAL_NERVE_MESH_PATH_6108_right, vis.config.CHORDA_MESH_PATH_6108_right, vis.config.gt_pose_6108_right),
    (vis.config.IMAGE_PATH_632, vis.config.OSSICLES_MESH_PATH_632_right, vis.config.FACIAL_NERVE_MESH_PATH_632_right, vis.config.CHORDA_MESH_PATH_632_right, vis.config.gt_pose_632_right),
    (vis.config.IMAGE_PATH_6320, vis.config.OSSICLES_MESH_PATH_6320_right, vis.config.FACIAL_NERVE_MESH_PATH_6320_right, vis.config.CHORDA_MESH_PATH_6320_right, vis.config.gt_pose_6320_right),
    (vis.config.IMAGE_PATH_6329, vis.config.OSSICLES_MESH_PATH_6329_right, vis.config.FACIAL_NERVE_MESH_PATH_6329_right, vis.config.CHORDA_MESH_PATH_6329_right, vis.config.gt_pose_6329_right),
    (vis.config.IMAGE_PATH_6602, vis.config.OSSICLES_MESH_PATH_6602_right, vis.config.FACIAL_NERVE_MESH_PATH_6602_right, vis.config.CHORDA_MESH_PATH_6602_right, vis.config.gt_pose_6602_right),
    (vis.config.IMAGE_PATH_6751, vis.config.OSSICLES_MESH_PATH_6751_right, vis.config.FACIAL_NERVE_MESH_PATH_6751_right, vis.config.CHORDA_MESH_PATH_6751_right, vis.config.gt_pose_6751_right),
    # left ossicles
    (vis.config.IMAGE_PATH_6742, vis.config.OSSICLES_MESH_PATH_6742_left, vis.config.FACIAL_NERVE_MESH_PATH_6742_left, vis.config.CHORDA_MESH_PATH_6742_left, vis.config.gt_pose_6742_left),
    (vis.config.IMAGE_PATH_6087, vis.config.OSSICLES_MESH_PATH_6087_left, vis.config.FACIAL_NERVE_MESH_PATH_6087_left, vis.config.CHORDA_MESH_PATH_6087_left, vis.config.gt_pose_6087_left),
    ]
)  
def test_load_mesh(app, image_path, ossicles_path, facial_nerve_path, chorda_path, gt_pose):
    image_numpy = np.array(Image.open(image_path)) # (H, W, 3)
    app.load_image(image_numpy)
    app.set_reference('ossicles')
    app.set_transformation_matrix(gt_pose)
    app.load_meshes({'ossicles': ossicles_path, 'facial_nerve': facial_nerve_path, 'chorda': chorda_path})
    app.bind_meshes("ossicles", "g")
    app.bind_meshes("chorda", "h")
    app.bind_meshes("facial_nerve", "j")
    app.set_reference("ossicles")
    app.plot()

@pytest.mark.parametrize(
    "image_path, ossicles_path, facial_nerve_path, chorda_path, RT, mirror_objects, mirror_image",
    [# mirror left to right ossicles
    (vis.config.IMAGE_PATH_6742, vis.config.OSSICLES_MESH_PATH_6742_left, vis.config.FACIAL_NERVE_MESH_PATH_6742_left, vis.config.CHORDA_MESH_PATH_6742_left, np.eye(4), True, False),
    (vis.config.IMAGE_PATH_6742, vis.config.OSSICLES_MESH_PATH_6742_left, vis.config.FACIAL_NERVE_MESH_PATH_6742_left, vis.config.CHORDA_MESH_PATH_6742_left, vis.config.gt_pose_6742_left, True, True),
    (vis.config.IMAGE_PATH_6742, vis.config.OSSICLES_MESH_PATH_6742_left, vis.config.FACIAL_NERVE_MESH_PATH_6742_left, vis.config.CHORDA_MESH_PATH_6742_left, vis.config.gt_pose_6742_left, True, False),
    ]
)  
def test_load_mesh_mirror_ossicles(app, image_path, ossicles_path, facial_nerve_path, chorda_path, RT, mirror_objects, mirror_image):
    app.set_mirror_objects(mirror_objects)
    image_numpy = np.array(Image.open(image_path)) # (H, W, 3)
    if mirror_image:
        image_numpy = image_numpy[:, ::-1, ...]
    app.load_image(image_numpy)
    app.set_transformation_matrix(RT)
    app.load_meshes({'ossicles': ossicles_path})#, 'facial_nerve': facial_nerve_path, 'chorda': chorda_path})
    app.bind_meshes("ossicles", "g")
    app.bind_meshes("chorda", "h")
    app.bind_meshes("facial_nerve", "j")
    app.set_reference("ossicles")
    app.plot()

@pytest.mark.parametrize(
    "mesh_path, gt_pose, mirror_objects",
    [(vis.config.OSSICLES_MESH_PATH_455_right, vis.config.gt_pose_455_right, False),
    (vis.config.OSSICLES_MESH_PATH_5997_right, vis.config.gt_pose_5997_right, False), 
    (vis.config.OSSICLES_MESH_PATH_6088_right, vis.config.gt_pose_6088_right, False),
    (vis.config.OSSICLES_MESH_PATH_6108_right, vis.config.gt_pose_6108_right, False),
    (vis.config.OSSICLES_MESH_PATH_632_right, vis.config.gt_pose_632_right, False),
    (vis.config.OSSICLES_MESH_PATH_6320_right, vis.config.gt_pose_6320_right, False),
    (vis.config.OSSICLES_MESH_PATH_6329_right, vis.config.gt_pose_6329_right, False),
    (vis.config.OSSICLES_MESH_PATH_6602_right, vis.config.gt_pose_6602_right, False),
    (vis.config.OSSICLES_MESH_PATH_6751_right, vis.config.gt_pose_6751_right, False),
    
    (vis.config.OSSICLES_MESH_PATH_6742_left, vis.config.gt_pose_6742_left, False),
    (vis.config.OSSICLES_MESH_PATH_6742_left, vis.config.gt_pose_6742_left, True),
    ]
)
def test_render_scene(app, mesh_path, gt_pose, mirror_objects):
    app.set_register(True)
    app.set_mirror_objects(mirror_objects)
    app.set_transformation_matrix(gt_pose)
    app.load_meshes({'ossicles': mesh_path})
    image_np = app.render_scene(render_image=False, render_objects=['ossicles'])
    # point = (image_np[542, 946] / 255).astype('float32')
    plt.imshow(image_np)
    plt.show()
    print("hhh")
    
def test_save_plot(app):
    app.set_register(False)
    app.set_transformation_matrix(np.eye(4))
    image_numpy = np.array(Image.open(vis.config.IMAGE_PATH_5997)) # (H, W, 3)
    app.load_image(image_numpy)

    app.load_meshes({'ossicles': vis.config.OSSICLES_MESH_PATH_5997_right, 'facial_nerve': vis.config.FACIAL_NERVE_MESH_PATH_5997_right, 'chorda': vis.config.CHORDA_MESH_PATH_5997_right})

    app.bind_meshes("ossicles", "g")
    app.bind_meshes("chorda", "h")
    app.bind_meshes("facial_nerve", "j")
    app.set_reference("ossicles")
    image_np = app.plot()
    plt.imshow(image_np)
    plt.show() 

def test_generate_image(app):
    image_numpy = np.array(Image.open(vis.config.IMAGE_PATH_5997)) # (H, W, 3)
    image_np = app.render_scene(render_image=True, image_source=image_numpy)
    plt.imshow(image_np); plt.show()

@pytest.mark.parametrize(
    "name, hand_draw_mask, ossicles_path, RT, resize, mirror_objects",
    [("455", None, vis.config.OSSICLES_MESH_PATH_455_right, vis.config.gt_pose_455_right, 1/10, False), # no resize: 0.05338873922462614 # resize 1/5 cv2: 0.026132524126728313 # if resize torch: 
        
    ("5997", None, vis.config.OSSICLES_MESH_PATH_5997_right, vis.config.gt_pose_5997_right, 1/10, False), # no resize: 0.021086712065792698 # resize 1/5 cv2: 0.020330257484100347 # if resize torch: 
    ("5997",  vis.config.mask_5997_hand_draw_numpy, vis.config.OSSICLES_MESH_PATH_5997_right, vis.config.gt_pose_5997_right, 1/10, False), # error: 1.3682088051366954 # if resize cv2: 1.0566890956912622 # if resize torch: 
    
    ("6088", None, vis.config.OSSICLES_MESH_PATH_6088_right, vis.config.gt_pose_6088_right, 1/10, False), # no resize: 5.491416579722634 # resize 1/5 cv2: 5.534377619304417 # if resize torch: 
    ("6088", vis.config.mask_6088_hand_draw_numpy, vis.config.OSSICLES_MESH_PATH_6088_right, vis.config.gt_pose_6088_right, 1/10, False), # error: 5.636555974411995 # if resize cv2: 5.46914034648768 # if resize torch: 
    
    ("6108", None, vis.config.OSSICLES_MESH_PATH_6108_right, vis.config.gt_pose_6108_right, 1/10, False), # no resize: 0.01895783336598894 # resize 1/5 cv2: 0.1413067780393649 # if resize torch: 
    ("6108", vis.config.mask_6108_hand_draw_numpy, vis.config.OSSICLES_MESH_PATH_6108_right, vis.config.gt_pose_6108_right, 1/10, False), # error: 0.3925129080313312 # if resize cv2: 22.451005863827966 # if resize torch: 
    
    ("6742", None, vis.config.OSSICLES_MESH_PATH_6742_left, vis.config.gt_pose_6742_left, 1/10, False), # no resize: 0.04155607588744 # resize 1/5 cv2: 0.13983189316096442 # if resize torch: 
    ("6742", vis.config.mask_6742_hand_draw_numpy, vis.config.OSSICLES_MESH_PATH_6742_left, vis.config.gt_pose_6742_left, 1/10, False), # error: 2.2111475894404378 # if resize cv2: 146.63621797086526 # if resize torch: 
    
    ("6742", None, vis.config.OSSICLES_MESH_PATH_6742_left, vis.config.gt_pose_6742_left, 1/10, True), # no resize: 5.214560773437986 # resize 1/5 cv2: 230.26984657453482 # if resize torch: 
    ]
)
def test_pnp_from_dataset(name, hand_draw_mask, ossicles_path, RT, resize, mirror_objects):

    # save the GT pose to .npy file
    # ossicles_side = ossicles_path.stem.split("_")[1]
    # gt_pose_name = f"{name}_{ossicles_side}_gt_pose.npy"
    # np.save(vis.config.DATA_DIR / "gt_pose" / gt_pose_name, RT)

    app = vis.App(register=True, scale=1, mirror_objects=mirror_objects)
    w, h = app.window_size

    if hand_draw_mask is not None: 
        seg_mask = np.load(hand_draw_mask).astype("bool")
        plt.imshow(seg_mask)
        plt.show()
    # no segmentation mask, use the whole mask to predict
    else: 
        seg_mask = np.ones((h, w)).astype("bool")

    if mirror_objects: seg_mask = seg_mask[..., ::-1]

    # expand the dimension
    seg_mask = np.expand_dims(seg_mask, axis=-1)
        
    app.set_transformation_matrix(RT)
    app.load_meshes({'ossicles': ossicles_path})
    app.plot()

    # Create rendering
    color_mask_whole = app.render_scene(render_image=False, render_objects=['ossicles'])
    # save the rendered whole image
    vis.utils.save_image(color_mask_whole, vis.config.DATA_DIR / "rendered_mask", f"rendered_mask_whole_{name}.png")

    color_mask_binarized = vis.utils.color2binary_mask(color_mask_whole)
    binary_mask = color_mask_binarized * seg_mask
    color_mask = (color_mask_whole * seg_mask).astype(np.uint8)
    assert (binary_mask == vis.utils.color2binary_mask(color_mask)).all(), "render_binary_mask is not the same as converted render_color_mask"

    # save the rendered partial image
    if hand_draw_mask is not None: vis.utils.save_image(color_mask, vis.config.DATA_DIR / "rendered_mask", f"rendered_mask_partial_{name}.png")
    
    # numpy implementation
    resize_height = int(h * resize)
    resize_width = int(w * resize)
    downscale_color_mask = cv2.resize(color_mask, (resize_width, resize_height), interpolation=cv2.INTER_AREA)
    downscale_binary_mask = cv2.resize(binary_mask, (resize_width, resize_height), interpolation=cv2.INTER_AREA)
        
    # based on the ratio of the mask size compare with the whole image
    if np.sum(downscale_binary_mask) / (downscale_binary_mask.shape[0] * downscale_binary_mask.shape[1]) > 0.01:
        color_mask = cv2.resize(downscale_color_mask, (w, h), interpolation=cv2.INTER_LINEAR)
        binary_mask = cv2.resize(downscale_binary_mask, (w, h), interpolation=cv2.INTER_LINEAR)
    else:
        color_mask = cv2.resize(downscale_color_mask, (w, h), interpolation=cv2.INTER_AREA)
        binary_mask = cv2.resize(downscale_binary_mask, (w, h), interpolation=cv2.INTER_AREA)
    # # torch implementation
    # trans = torchvision.transforms.Resize((h, w))
    # color_mask = trans(torch.tensor(downscale_color_mask).permute(2,0,1))
    # color_mask = color_mask.permute(1,2,0).detach().cpu().numpy()
    # binary_mask = trans(torch.tensor(downscale_binary_mask).unsqueeze(-1).permute(2,0,1))
    # binary_mask = binary_mask.permute(1,2,0).squeeze().detach().cpu().numpy()
    # make sure the binary mask only contains 0 and 1
    binary_mask = np.where(binary_mask != 0, 1, 0)
    binary_mask_bool = binary_mask.astype('bool')
    assert (binary_mask == binary_mask_bool).all(), "binary mask should be the same as binary mask bool"

    plt.subplot(221)
    plt.imshow(color_mask_whole)
    plt.subplot(222)
    plt.imshow(seg_mask)
    plt.subplot(223)
    plt.imshow(binary_mask)
    plt.subplot(224)
    plt.imshow(color_mask)
    plt.show()
    
    # Create 2D-3D correspondences
    vertices = getattr(app, f'ossicles_vertices')
    pts2d, pts3d = vis.utils.create_2d_3d_pairs(color_mask, vertices) #, binary_mask=binary_mask)
    
    logger.debug(f"The total points are {pts3d.shape[0]}")

    predicted_pose = vis.utils.solve_epnp_cv2(pts2d, pts3d, app.camera_intrinsics, app.camera.position)

    if mirror_objects: predicted_pose = np.array([[-1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]) @ predicted_pose @ np.array([[-1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
            
    logger.debug(f"\ndifference from predicted pose and RT pose: {np.sum(np.abs(predicted_pose - RT))}")
            
    assert np.isclose(predicted_pose, RT, atol=20).all()