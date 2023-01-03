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

import vision6D as vis

logger = logging.getLogger("vision6D")

np.set_printoptions(suppress=True)

CWD = pathlib.Path(os.path.abspath(__file__)).parent
DATA_DIR = CWD / 'data'
IMAGE_PATH = DATA_DIR / "image.jpg"
BACKGROUND_PATH = DATA_DIR / "black_background.jpg"
MASK_PATH_NUMPY_FULL = DATA_DIR / "segmented_mask_numpy.npy"
MASK_PATH_NUMPY_QUARTER = DATA_DIR / "quarter_image_mask_numpy.npy"
MASK_PATH_NUMPY_SMALLEST = DATA_DIR / "smallest_image_mask_numpy.npy"
STANDARD_LENS_MASK_PATH_NUMPY = DATA_DIR / "test1.npy"

OSSICLES_PATH = DATA_DIR / "ossicles_001_colored_not_centered.ply"
FACIAL_NERVE_PATH = DATA_DIR / "facial_nerve_001_colored_not_centered.ply"
CHORDA_PATH = DATA_DIR / "chorda_001_colored_not_centered.ply"

OSSICLES_PATH_NO_COLOR = DATA_DIR / "ossicles_001_not_colored.ply"
FACIAL_NERVE_PATH_NO_COLOR = DATA_DIR / "facial_nerve_001_not_colored.ply"
CHORDA_PATH_NO_COLOR = DATA_DIR / "chorda_001_not_colored.ply"

OSSICLES_MESH_PATH = DATA_DIR / "5997_right_output_mesh_from_df.mesh"
FACIAL_NERVE_MESH_PATH = DATA_DIR / "5997_right_facial_nerve.mesh"
CHORDA_MESH_PATH = DATA_DIR / "5997_right_chorda.mesh"

OSSICLES_TRANSFORMATION_MATRIX = np.array([[  0.08788493,  -0.49934587,  -0.86193385,  -1.73198707],
                                            [  0.61244989,   0.70950026,  -0.34858929, -25.0914638 ],
                                            [  0.78560891,  -0.49725556,   0.3681787,    0.43013393],
                                            [  0.,           0.,           0.,           1.        ]]) #  GT pose

# OSSICLES_TRANSFORMATION_MATRIX = np.array([[     0.7565,     -0.5291,      0.3845,     16.1959],
#          [     0.5796,      0.8147,     -0.0193,    -18.4053],
#          [    -0.3031,      0.2375,      0.9229,   -438.4466],
#          [     0.0000,      0.0000,      0.0000,      1.0000]])

# OSSICLES_TRANSFORMATION_MATRIX = np.array([[     0.0929,     -0.5055,     -0.8578,     -0.9356],
#                                     [     0.6765,      0.6642,     -0.3181,    -24.1057],
#                                     [     0.7306,     -0.5507,      0.4037,   -457.9619],
#                                     [     0.0000,      0.0000,      0.0000,      1.0000]])

# OSSICLES_TRANSFORMATION_MATRIX = np.array([[  0.0900,  -0.4999,  -0.8614,  -1.6455],
#                                     [  0.6185,   0.7060,  -0.3451, -24.9873],
#                                     [  0.7806,  -0.5017,   0.3728,  -7.1757],
#                                     [  0.0000,   0.0000,   0.0000,   1.0000]]) #  predicted from pytorch3d


# OSSICLES_TRANSFORMATION_MATRIX = np.array([[  0.37177922,   0.8300953,   -0.41559835, -24.30279375],
#                                             [  0.51533184,  -0.5569185,   -0.65136388,  -4.5669351],
#                                             [ -0.7721485,    0.0279925,   -0.63482527,  -3.57181275],
#                                             [  0.,           0.,           0.,           1.,        ]]) #  GT pose

# OSSICLES_TRANSFORMATION_MATRIX = np.array([[     0.3468,      0.8284,     -0.4399,    -24.6587],
#                                         [     0.4898,     -0.5599,     -0.6682,     -4.6086],
#                                         [    -0.7998,      0.0163,     -0.6000,     26.7000],
#                                         [     0.0000,      0.0000,      0.0000,      1.0000]]) #  predicted from pytorch3d

# OSSICLES_TRANSFORMATION_MATRIX = np.array([[  0.08788493,  -0.49934587,  -0.86193385,  -2.28768117],
#                                         [  0.61244989,   0.70950026,  -0.34858929, -25.39078897],
#                                         [  0.78560891,  -0.49725556,   0.3681787,    0.43013393],
#                                         [  0.,           0.,           0.,           1.        ]]) #  GT pose

# OSSICLES_TRANSFORMATION_MATRIX = np.array([[  0.0869,  -0.5010,  -0.8611,  -2.0267],
#                                         [  0.6084,   0.7111,  -0.3524, -25.3319],
#                                         [  0.7888,  -0.4933,   0.3667, -16.5832],
#                                         [  0.0000,   0.0000,   0.0000,   1.0000]]) # predicted from pytorch3d

# OSSICLES_TRANSFORMATION_MATRIX = np.array([[  0.08725841,  -0.49920268,  -0.86208042,  -1.773618  ],
#                                 [  0.61232186,   0.7094788 ,  -0.34885781, -25.13447245],
#                                 [  0.78577854,  -0.49742991,   0.3675807 ,   2.70771307],
#                                 [  0.        ,   0.        ,   0.        ,   1.        ]]) # GT pose

# OSSICLES_TRANSFORMATION_MATRIX = np.array([[  0.0926,  -0.5013,  -0.8603,  -1.6665],
#                             [  0.6176,   0.7067,  -0.3453, -25.0299],
#                             [  0.7811,  -0.4993,   0.3750,  -5.6169],
#                             [  0.0000,   0.0000,   0.0000,   1.0000]]) # predicted pose

# OSSICLES_TRANSFORMATION_MATRIX = np.array([[  0.08771557,  -0.49943043,  -0.8619021 ,  -1.75110001],
#                                 [  0.61228039,   0.70952996,  -0.34882654, -25.11469416],
#                                 [  0.78575995,  -0.49712824,   0.36802828,   1.49357594],
#                                 [  0.        ,   0.        ,   0.        ,   1.        ]]) # GT pose

# OSSICLES_TRANSFORMATION_MATRIX = np.array([[  0.0905,  -0.5002,  -0.8611,  -1.6447],
#                                     [  0.6181,   0.7062,  -0.3453, -25.0012],
#                                     [  0.7809,  -0.5010,   0.3731,  -7.7220],
#                                     [  0.0000,   0.0000,   0.0000,   1.0000]]) # predicted pose

# full size of the (1920, 1080)
@pytest.fixture
def app_full():
    return vis.App(register=True, 
                  width=1920, 
                  height=1080, 
                  cam_focal_length=5e+4, 
                  cam_position=(9.6, 5.4, -500), 
                  cam_focal_point=(9.6, 5.4, 0),
                  cam_viewup=(0,-1,0))
    
# 1/4 size of the (1920, 1080)
@pytest.fixture
def app_quarter():
    return vis.App(register=True, 
                  width=480, 
                  height=270, 
                  cam_focal_length=5e+4, 
                  cam_position=(9.6, 5.4, -2000), 
                  cam_focal_point=(9.6, 5.4, 0),
                  cam_viewup=(0,-1,0))
    
@pytest.fixture
def app_smallest():
    return vis.App(register=True, 
                  width=240, 
                  height=135, 
                  cam_focal_length=5e+4, 
                  cam_position=(9.6, 5.4, -4000), 
                  cam_focal_point=(9.6, 5.4, 0),
                  cam_viewup=(0,-1,0))
    
@pytest.mark.parametrize(
    "app",
    [lazy_fixture("app_full"), lazy_fixture("app_quarter"), lazy_fixture("app_smallest")]
)  
def test_load_mesh(app):
    app.load_image(IMAGE_PATH, [0.01, 0.01, 1])
    app.set_transformation_matrix(OSSICLES_TRANSFORMATION_MATRIX)
    app.load_meshes({'ossicles': OSSICLES_PATH_NO_COLOR, 'facial_nerve': FACIAL_NERVE_PATH_NO_COLOR, 'chorda': CHORDA_PATH_NO_COLOR})
    app.bind_meshes("ossicles", "g")
    app.bind_meshes("chorda", "h")
    app.bind_meshes("facial_nerve", "j")
    app.set_reference("ossicles")
    app.plot()
    
@pytest.mark.parametrize(
    "app",
    [lazy_fixture("app_full"), lazy_fixture("app_quarter"), lazy_fixture("app_smallest")]
)  
def test_generate_image(app):
    if app.camera.position == (9.6, 5.4, -500):
        name = "full"
    elif app.camera.position == (9.6, 5.4, -2000):
        name = "quarter"
    elif app.camera.position == (9.6, 5.4, -4000):
        name = "smallest"
    image_np = app.render_scene(IMAGE_PATH, [0.01, 0.01, 1], True)
    vis.utils.save_image(image_np, DATA_DIR, f"image_{name}.png")
    print(image_np)

@pytest.mark.parametrize(
    "RT",
    [
        (np.array([[  0.03292723,  -0.19892261,  -0.97946189 , -9.58437769],
                [  0.26335909 ,  0.94708607,  -0.18349376, -22.55842936],
                [  0.96413577,  -0.25190826,   0.083573,   -14.69781384],
                [  0.,           0.,           0.,           1.        ]])),
        (np.array([[  0.08788493,  -0.49934587,  -0.86193385,  -1.73198707],
                    [  0.61244989,   0.70950026,  -0.34858929, -25.0914638 ],
                    [  0.78560891,  -0.49725556,   0.3681787,    0.43013393],
                    [  0.,           0.,           0.,           1.        ]]))
    ]
)
def test_pnp_with_ossicles_surgical_microscope_quarter_size(app_quarter, RT):
    
    app = app_quarter
   
    app.set_transformation_matrix(RT)
    app.load_meshes({'ossicles': OSSICLES_PATH_NO_COLOR})
    app.plot()
    
    # Create rendering
    render_white_bg = app.render_scene(BACKGROUND_PATH, (0.01, 0.01, 1), render_image=False, render_objects=['ossicles'])
    render_black_bg = vis.utils.change_mask_bg(render_white_bg, [255, 255, 255], [0, 0, 0])
    mask_render = vis.utils.color2binary_mask(render_black_bg)
    
    plt.subplot(221)
    plt.imshow(render_white_bg)
    plt.subplot(222)
    plt.imshow(render_black_bg)
    plt.subplot(223)
    plt.imshow(mask_render)
    plt.show()
    
    # Create 2D-3D correspondences
    pts2d, pts3d = vis.utils.create_2d_3d_pairs(mask_render, render_black_bg, app, 'ossicles')
    
    logger.debug(f"The total points are {pts3d.shape[0]}")

    pts2d = pts2d.astype('float32')
    pts3d = pts3d.astype('float32')
    camera_intrinsics = app.camera_intrinsics.astype('float32')
    
    if pts2d.shape[0] < 4:
        predicted_pose = np.eye(4)
        inliers = []
    else:
        dist_coeffs = np.zeros((4, 1))
        success, rotation_vector, translation_vector, inliers = cv2.solvePnPRansac(pts3d, pts2d, camera_intrinsics, dist_coeffs, confidence=0.999, flags=cv2.SOLVEPNP_EPNP)
        
        # Get a rotation matrix
        predicted_pose = np.eye(4)
        if success:
            predicted_pose[:3, :3] = cv2.Rodrigues(rotation_vector)[0]
            predicted_pose[:3, 3] = np.squeeze(translation_vector) + app.camera.position
            logger.debug(len(inliers))
            
    assert np.isclose(predicted_pose, RT, atol=1).all()
    
@pytest.mark.parametrize(
    "RT",
    [
        (np.array([[  0.08788493,  -0.49934587,  -0.86193385,  -1.73198707],
                    [  0.61244989,   0.70950026,  -0.34858929, -25.0914638 ],
                    [  0.78560891,  -0.49725556,   0.3681787,    0.43013393],
                    [  0.,           0.,           0.,           1.        ]])),
        (np.array([[  0.05564547,  -0.42061121,  -0.90553289,  -3.67169989],
                [  0.5665481,    0.76009545,  -0.31824226, -24.86456215],
                [  0.82214769,  -0.49531921,   0.28059234,  -1.65629749],
                [  0.,           0.,           0.,           1.        ]])),
        (np.array([[ -0.04368987,  -0.36370424,  -0.93048935,  -4.26740943],
                [  0.43051434,   0.8336103,   -0.34605094, -25.10016632],
                [  0.9015257,   -0.41570794,   0.12015956,  -7.1369013 ],
                [  0.,           0.,           0.,           1.        ]])),
        (np.array([[ -0.21403014,  -0.24968077,  -0.94437843,  -3.71577383],
                [  0.12515886,   0.95180355,  -0.28000937, -22.70262825],
                [  0.9687757,   -0.17812778,  -0.17246489, -17.75878025],
                [  0.,           0.,           0.,           1.        ]])),
        (np.array([[  0.03292723,  -0.19892261,  -0.97946189 , -9.58437769],
                [  0.26335909 ,  0.94708607,  -0.18349376, -22.55842936],
                [  0.96413577,  -0.25190826,   0.083573,   -14.69781384],
                [  0.,           0.,           0.,           1.        ]])),
        (np.array([[ -0.14574589,  -0.18814922,  -0.97126619,  -5.90455811],
                [  0.30022033,   0.92704254,  -0.22463276, -23.03902215],
                [  0.94266955,  -0.32433316,  -0.07862642, -12.92929744],
                [  0.,           0.,           0.,           1.        ]])),
        (np.array([[  0.43571207,   0.77372648,  -0.45989382, -24.09672039],
                    [  0.35232826,  -0.61678406,  -0.70387657,  -2.90416953],
                    [ -0.82826311,   0.14465392,  -0.54134597,  -3.38633483],
                    [  0.,           0.,           0.,           1.        ]])),
        (np.array([[ -0.14677223,  -0.10625233,  -0.98344718,  -8.07226061],
                [  0.08478254,   0.98920427,  -0.11952749, -19.49734302],
                [  0.98553023,  -0.10092246,  -0.13617937, -21.66010952],
                [  0.,           0.,           0.,           1.        ]])),
        # (np.array([[  0.92722934,  -0.1715687,    0.33288124,   0.76798202],
        #     [ -0.25051527,  -0.94488288,   0.21080426,  27.04220591],
        #     [  0.27836637,  -0.27885573,  -0.91910372, -18.25491242],
        #     [  0.,           0.,           0.,           1.        ]])),
        # (np.array([[  0.29220856,   0.88228889,   0.36902639,  -7.69347165],
        #         [  0.75469319,   0.02427374,  -0.65562868, -23.58010659],
        #         [ -0.58741155,   0.47008203,  -0.65876442, -15.3083587 ],
        #         [  0.,           0.,           0.,           1.        ]])),
        # (np.array([[  0.15904642,  -0.55171761,   0.81872579,  27.86719635],
        #         [  0.8514174,    0.49646224,   0.16915564, -16.26150026],
        #         [ -0.49979259,   0.6701738,    0.54870253,   0.20008692],
        #         [  0.,           0.,           0.,           1.        ]])),
        # (np.array([[  0.26894049,  -0.68035947,  -0.68174924,   3.35767679],
        #         [  0.95884839,   0.12225034,   0.25625106, -10.48357013],
        #         [ -0.09099875,  -0.72261044,   0.68523965,  23.3685089 ],
        #         [  0.,           0.,           0.,           1.        ]])), # not working, not enough points ~ 3000 points
        # (np.array([[  0.26894049,  -0.68035947,  -0.68174924,   2.44142936],
        #         [  0.95884839,   0.12225034,   0.25625106, -10.72797506],
        #         [ -0.09099875,  -0.72261044,   0.68523965,  23.3685089 ],
        #         [  0.,           0.,           0.,           1.        ]])), # working, enough points ~30000 points
        # (np.array([[ 0.35085479, -0.77589796, -0.52429314,  5.67395223],
        #         [ 0.89913432,  0.12269361,  0.42012348, -7.56528092],
        #         [-0.26164552, -0.61881228,  0.74068412, 24.86819684],
        #         [ 0.,          0.,          0.,          1.        ]])),
        # (np.array([[  0.27405315,  -0.95999139,   0.0575449,   23.07934883],
        #             [  0.90607829,   0.2376796,   -0.35004359, -18.89619621],
        #             [  0.32236158,   0.14807074,   0.93496421,   4.59932613],
        #             [  0.,           0.,           0.,           1.        ]])), # not very accurate
        # (np.array([[  0.27405315,  -0.95999139,   0.0575449,   21.31368812],
        #         [  0.90607829,   0.2376796,   -0.35004359, -19.70032993],
        #         [  0.32236158,   0.14807074,   0.93496421,   4.69378537],
        #         [  0.,           0.,           0.,           1.        ]])), # accurate
        # (np.array([[  0.13475468,   0.82180511,  -0.55360414, -20.35367606],
        #         [  0.92092791,   0.10232293,   0.37606089,  -7.7183049 ],
        #         [  0.36569516,  -0.56050548,  -0.74303478, -11.09524467],
        #         [  0.,           0.,           0.,           1.        ]])), # not very accurate ~ 10000 points
        # (np.array([[  0.13475468,   0.82180511,  -0.55360414, -21.0793958 ],
        #         [  0.92092791,   0.10232293,   0.37606089,  -7.7333164 ],
        #         [  0.36569516,  -0.56050548,  -0.74303478, -11.09524467],
        #         [  0.,           0.,           0.,           1.        ]])) # accurate ~40000 points
    ])
def test_pnp_with_masked_ossicles_surgical_microscope_smallest_size(app_smallest, RT):
    app = app_smallest
    mask = np.load(MASK_PATH_NUMPY_SMALLEST) / 255 # read image path: DATA_DIR / "ossicles_mask.png"
   
    mask = np.where(mask != 0, 1, 0)
   
    # expand the dimension
    ossicles_mask = np.expand_dims(mask, axis=-1)
   
    # Dilate mask
    # mask = cv2.dilate(mask, np.ones((5,5),np.uint8), iterations = 100)
        
    app.set_transformation_matrix(RT)
    app.load_meshes({'ossicles': OSSICLES_PATH_NO_COLOR})
    app.plot()
    
    # Create rendering
    render_white_bg = app.render_scene(BACKGROUND_PATH, (0.01, 0.01, 1), render_image=False, render_objects=['ossicles'])
    render_black_bg = vis.utils.change_mask_bg(render_white_bg, [255, 255, 255], [0, 0, 0])
    # save the rendered whole image
    vis.utils.save_image(render_black_bg, DATA_DIR, "rendered_mask_whole_smallest.png")
    mask_render = vis.utils.color2binary_mask(render_black_bg)
    mask_render_masked = mask_render * ossicles_mask
    render_masked_black_bg = (render_black_bg * ossicles_mask).astype(np.uint8)  # render_masked_white_bg = render_white_bg * ossicles_mask
    # save the rendered partial image
    vis.utils.save_image(render_masked_black_bg, DATA_DIR, "rendered_mask_partial_smallest.png")
    
    plt.subplot(221)
    plt.imshow(render_black_bg)
    plt.subplot(222)
    plt.imshow(ossicles_mask)
    plt.subplot(223)
    plt.imshow(mask_render_masked)
    plt.subplot(224)
    plt.imshow(render_masked_black_bg)
    plt.show()
    
    # Create 2D-3D correspondences
    # pts2d, pts3d = vis.utils.create_2d_3d_pairs(mask_render_masked, render_masked_black_bg, app, 'ossicles', npts=30)
    pts2d, pts3d = vis.utils.create_2d_3d_pairs(mask_render_masked, render_masked_black_bg, app, 'ossicles')
    
    logger.debug(f"The total points are {pts3d.shape[0]}")

    pts2d = pts2d.astype('float32')
    pts3d = pts3d.astype('float32')
    camera_intrinsics = app.camera_intrinsics.astype('float32')
    
    if pts2d.shape[0] < 4:
        predicted_pose = np.eye(4)
        inliers = []
    else:
        dist_coeffs = np.zeros((4, 1))
        
        # Get a rotation matrix
        predicted_pose = np.eye(4)
        
        # Use EPNP
        success, rotation_vector, translation_vector, inliers = cv2.solvePnPRansac(pts3d, pts2d, camera_intrinsics, dist_coeffs, confidence=0.999, flags=cv2.SOLVEPNP_EPNP)
            
        if success:
            predicted_pose[:3, :3] = cv2.Rodrigues(rotation_vector)[0]
            predicted_pose[:3, 3] = np.squeeze(translation_vector) + np.array(app.camera.position)
            logger.debug(len(inliers)) # 50703
            
    logger.debug(f"\ndifference from predicted pose and RT pose: {np.sum(np.abs(predicted_pose - RT))}")
            
    assert np.isclose(predicted_pose, RT, atol=20).all()
     
@pytest.mark.parametrize(
    "app, RT",
    [
        (lazy_fixture("app_full"), np.array([[  0.08788493,  -0.49934587,  -0.86193385,  -1.73198707],
                    [  0.61244989,   0.70950026,  -0.34858929, -25.0914638 ],
                    [  0.78560891,  -0.49725556,   0.3681787,    0.43013393],
                    [  0.,           0.,           0.,           1.        ]])),
        (lazy_fixture("app_quarter"), np.array([[  0.08788493,  -0.49934587,  -0.86193385,  -1.73198707],
                    [  0.61244989,   0.70950026,  -0.34858929, -25.0914638 ],
                    [  0.78560891,  -0.49725556,   0.3681787,    0.43013393],
                    [  0.,           0.,           0.,           1.        ]])),
        (lazy_fixture("app_smallest"), np.array([[  0.08788493,  -0.49934587,  -0.86193385,  -1.73198707],
                    [  0.61244989,   0.70950026,  -0.34858929, -25.0914638 ],
                    [  0.78560891,  -0.49725556,   0.3681787,    0.43013393],
                    [  0.,           0.,           0.,           1.        ]])),
        # (lazy_fixture("app_full"), np.array([[  0.37177922,   0.8300953,   -0.41559835, -24.30279375],
        #             [  0.51533184,  -0.5569185,   -0.65136388,  -4.5669351],
        #             [ -0.7721485,    0.0279925,   -0.63482527,  -3.57181275],
        #             [  0.,           0.,           0.,           1.,        ]])),
        # (lazy_fixture("app_full"),  np.array([[  0.08788493,  -0.49934587,  -0.86193385,  -2.28768117],
        #             [  0.61244989,   0.70950026,  -0.34858929, -25.39078897],
        #             [  0.78560891,  -0.49725556,   0.3681787,    0.43013393],
        #             [  0.,           0.,           0.,           1.        ]])),
        # (lazy_fixture("app_full"),   np.array([[  0.08725841,  -0.49920268,  -0.86208042,  -1.773618  ],
        #                         [  0.61232186,   0.7094788 ,  -0.34885781, -25.13447245],
        #                         [  0.78577854,  -0.49742991,   0.3675807 ,   2.70771307],
        #                         [  0.        ,   0.        ,   0.        ,   1.        ]]))
        # (lazy_fixture("app_full"),   np.array([[  0.08771557,  -0.49943043,  -0.8619021 ,  -1.75110001],
        #                         [  0.61228039,   0.70952996,  -0.34882654, -25.11469416],
        #                         [  0.78575995,  -0.49712824,   0.36802828,   1.49357594],
        #                         [  0.        ,   0.        ,   0.        ,   1.        ]]))
    ]
)
def test_pnp_with_masked_ossicles_surgical_microscope(app, RT):
    
    mask_full = np.load(MASK_PATH_NUMPY_FULL)
    
    if app.camera.position == (9.6, 5.4, -500):
    #    mask = np.load(MASK_PATH_NUMPY_FULL) / 255
        name = "full"
        mask = mask_full / 255
        mask = np.where(mask != 0, 1, 0)
    elif app.camera.position == (9.6, 5.4, -2000):
    #     mask = np.load(MASK_PATH_NUMPY_QUARTER) / 255
        name = "quarter"
        mask = skimage.transform.rescale(mask_full, 1/4)
        mask = np.where(mask > 0.1, 1, 0)
    elif app.camera.position == (9.6, 5.4, -4000):
    #     mask = np.load(MASK_PATH_NUMPY_SMALLEST) / 255
        name = "smallest"
        mask = skimage.transform.rescale(mask_full, 1/8)
        # mask = np.where(mask > 0.1, 1, 0)
        mask = np.where(mask > 0.1, 1, 0)
        
    plt.subplot(211)
    plt.imshow(mask_full)
    plt.subplot(212)
    plt.imshow(mask)
    plt.show()
   
    # expand the dimension
    ossicles_mask = np.expand_dims(mask, axis=-1)
   
    # Dilate mask
    # mask = cv2.dilate(mask, np.ones((5,5),np.uint8), iterations = 100)
        
    app.set_transformation_matrix(RT)
    app.load_meshes({'ossicles': OSSICLES_PATH_NO_COLOR})
    app.plot()
    
    # Create rendering
    render_white_bg = app.render_scene(BACKGROUND_PATH, (0.01, 0.01, 1), render_image=False, render_objects=['ossicles'])
    render_black_bg = vis.utils.change_mask_bg(render_white_bg, [255, 255, 255], [0, 0, 0])
    # save the rendered whole image
    vis.utils.save_image(render_black_bg, DATA_DIR, f"rendered_mask_whole_{name}.png")
    mask_render = vis.utils.color2binary_mask(render_black_bg)
    mask_render_masked = mask_render * ossicles_mask
    render_masked_black_bg = (render_black_bg * ossicles_mask).astype(np.uint8)  # render_masked_white_bg = render_white_bg * ossicles_mask
    # save the rendered partial image
    vis.utils.save_image(render_masked_black_bg, DATA_DIR, f"rendered_mask_partial_{name}.png")
    assert (mask_render_masked == vis.utils.color2binary_mask(render_masked_black_bg)).all()
    
    plt.subplot(221)
    plt.imshow(render_black_bg)
    plt.subplot(222)
    plt.imshow(ossicles_mask)
    plt.subplot(223)
    plt.imshow(mask_render_masked)
    plt.subplot(224)
    plt.imshow(render_masked_black_bg)
    plt.show()
    
    # Create 2D-3D correspondences
    # pts2d, pts3d = vis.utils.create_2d_3d_pairs(mask_render_masked, render_masked_black_bg, app, 'ossicles', npts=30)
    pts2d, pts3d = vis.utils.create_2d_3d_pairs(mask_render_masked, render_masked_black_bg, app, 'ossicles')
    
    logger.debug(f"The total points are {pts3d.shape[0]}")

    pts2d = pts2d.astype('float32')
    pts3d = pts3d.astype('float32')
    camera_intrinsics = app.camera_intrinsics.astype('float32')
    
    if pts2d.shape[0] < 4:
        predicted_pose = np.eye(4)
        inliers = []
    else:
        dist_coeffs = np.zeros((4, 1))
        
        # Get a rotation matrix
        predicted_pose = np.eye(4)
        
        # Use EPNP
        success, rotation_vector, translation_vector, inliers = cv2.solvePnPRansac(pts3d, pts2d, camera_intrinsics, dist_coeffs, confidence=0.999, flags=cv2.SOLVEPNP_EPNP)
            
        if success:
            predicted_pose[:3, :3] = cv2.Rodrigues(rotation_vector)[0]
            predicted_pose[:3, 3] = np.squeeze(translation_vector) + np.array(app.camera.position)
            logger.debug(len(inliers)) # 50703
            
    logger.debug(f"\ndifference from predicted pose and RT pose: {np.sum(np.abs(predicted_pose - RT))}")
            
    assert np.isclose(predicted_pose, RT, atol=4).all()