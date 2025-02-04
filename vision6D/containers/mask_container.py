'''
@author: Yike (Nicole) Zhang
@license: (C) Copyright.
@contact: yike.zhang@vanderbilt.edu
@software: Vision6D
@file: mask_container.py
@time: 2023-07-03 20:26
@desc: create container for mask related actions in application
'''

import pathlib

import numpy as np
import pyvista as pv
import PIL.Image

from PyQt5 import QtWidgets

from ..tools import utils
from ..components import CameraStore
from ..components import ImageStore
from ..components import MaskStore
from ..widgets import LabelWindow

class MaskContainer:
    def __init__(self, 
                plotter, 
                hintLabel, 
                track_actors_names, 
                add_button_actor_name, 
                check_button,
                output_text):

        self.plotter = plotter
        self.hintLabel = hintLabel
        self.track_actors_names = track_actors_names
        self.add_button_actor_name = add_button_actor_name
        self.check_button = check_button
        self.output_text = output_text

        self.camera_store = CameraStore()
        self.image_store = ImageStore()
        self.mask_store = MaskStore()

    def add_mask_file(self, mask_path='', prompt=False):
        if prompt:
            mask_path, _ = QtWidgets.QFileDialog().getOpenFileName(None, "Open file", "", "Files (*.png *.jpg *.jpeg *.tiff *.bmp *.webp *.ico)") 
        if mask_path:
            self.hintLabel.hide()
            self.add_mask(mask_path)

    def mirror_mask(self, direction):
        if direction == 'x': self.mask_store.mirror_x = not self.mask_store.mirror_x
        elif direction == 'y': self.mask_store.mirror_y = not self.mask_store.mirror_y
        self.add_mask(self.mask_store.mask_path)

    def load_mask(self, mask_surface, points):
        # Add mask surface object to the plot
        mask_mesh = self.plotter.add_mesh(mask_surface, color="white", style='surface', opacity=self.mask_store.mask_opacity)
        actor, _ = self.plotter.add_actor(mask_mesh, pickable=True, name='mask')
        self.mask_store.mask_actor = actor
        mask_point_data = utils.get_mask_actor_points(self.mask_store.mask_actor)
        assert np.isclose(((mask_point_data+self.mask_store.mask_bottom_point-self.mask_store.mask_offset) - points), 0).all(), "mask_point_data and points should be equal"

    def add_mask(self, mask_source):
        mask_surface, points = self.mask_store.add_mask(mask_source)
        self.load_mask(mask_surface, points)
        
        # Add remove current image to removeMenu
        if 'mask' not in self.track_actors_names:
            self.track_actors_names.append('mask')
            self.add_button_actor_name('mask')
    
    def reset_mask(self):
        if self.mask_store.mask_path:
            mask_surface, points = self.mask_store.add_mask(self.mask_store.mask_path)
            self.load_mask(mask_surface, points)

    def set_mask_opacity(self, mask_opacity: float):
        self.mask_store.mask_opacity = mask_opacity
        self.mask_store.mask_actor.GetProperty().opacity = mask_opacity
        self.plotter.add_actor(self.mask_store.mask_actor, pickable=True, name='mask')
    
    def toggle_mask_opacity(self, up):
        change = 0.05
        if not up: change *= -1
        self.mask_store.update_opacity(change)
        self.plotter.add_actor(self.mask_store.mask_actor, pickable=True, name="mask")
        self.check_button(actor_name='mask')
    
    def draw_mask(self):
        def handle_output_path_change(output_path):
            if output_path:
                self.mask_store.mask_path = output_path
                self.add_mask(self.mask_store.mask_path)
        if self.image_store.image_path:
            self.label_window = LabelWindow(self.image_store.image_path)
            self.label_window.show()
            self.label_window.image_label.output_path_changed.connect(handle_output_path_change)
        else:
            QtWidgets.QMessageBox.warning(QtWidgets.QMainWindow(), 'vision6D', "Need to load an image first!", QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
            return 0

    def export_mask(self):
        if self.mask_store.mask_actor:
            # Store the transformed mask actor if there is any transformation
            mask_surface = self.mask_store.update_mask()
            mask_mesh = self.plotter.add_mesh(mask_surface, color="white", style='surface', opacity=self.mask_store.mask_opacity)
            actor, _ = self.plotter.add_actor(mask_mesh, pickable=True, name='mask')
            self.mask_store.mask_actor = actor

            image = self.mask_store.render_mask(camera=self.plotter.camera.copy())
            output_path, _ = QtWidgets.QFileDialog.getSaveFileName(QtWidgets.QMainWindow(), "Save File", "", "Mask Files (*.png)")
            if output_path:
                if pathlib.Path(output_path).suffix == '': output_path = output_path.parent / (output_path.stem + '.png')
                rendered_image = PIL.Image.fromarray(image)
                rendered_image.save(output_path)
                self.output_text.append(f"-> Export mask render to:\n {str(output_path)}")
                self.output_text.append(f"\n************************************************************\n")
        else:
            QtWidgets.QMessageBox.warning(QtWidgets.QMainWindow(), 'vision6D', "Need to load a mask first!", QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
            return 0