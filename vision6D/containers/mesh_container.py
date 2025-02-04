'''
@author: Yike (Nicole) Zhang
@license: (C) Copyright.
@contact: yike.zhang@vanderbilt.edu
@software: Vision6D
@file: mesh_container.py
@time: 2023-07-03 20:27
@desc: create container for mesh related actions in application
'''

import ast
import copy
import pathlib

import trimesh
import PIL.Image
import numpy as np
import pyvista as pv

from PyQt5 import QtWidgets

from ..tools import utils
from ..components import CameraStore
from ..components import MaskStore
from ..components import MeshStore
from ..widgets import GetTextDialog

class MeshContainer:
    def __init__(self, 
                color_button, 
                plotter, 
                hintLabel, 
                track_actors_names, 
                add_button_actor_name, 
                button_group_actors_names,
                check_button,
                opacity_spinbox, 
                opacity_value_change,
                reset_camera,
                current_pose,
                register_pose,
                output_text):
        
        self.ignore_opacity_change = False
        self.toggle_hide_meshes_flag = False

        self.color_button = color_button
        self.plotter = plotter
        self.hintLabel = hintLabel
        self.track_actors_names = track_actors_names
        self.add_button_actor_name = add_button_actor_name
        self.button_group_actors_names = button_group_actors_names
        self.check_button = check_button
        self.opacity_spinbox = opacity_spinbox
        self.opacity_value_change = opacity_value_change
        self.reset_camera = reset_camera
        self.register_pose = register_pose
        self.current_pose = current_pose
        self.output_text = output_text
        
        self.camera_store = CameraStore()
        self.mask_store = MaskStore()
        self.mesh_store = MeshStore()

    def add_mesh_file(self, mesh_path='', prompt=False):
        if prompt: 
            mesh_path, _ = QtWidgets.QFileDialog().getOpenFileName(None, "Open file", "", "Files (*.mesh *.ply *.stl *.obj *.off *.dae *.fbx *.3ds *.x3d)") 
        if mesh_path:
            self.hintLabel.hide()
            self.add_mesh(mesh_path)

    def mirror_mesh(self, direction):
        if direction == 'x': self.mesh_store.mirror_x = not self.mesh_store.mirror_x
        elif direction == 'y': self.mesh_store.mirror_y = not self.mesh_store.mirror_y
        transformation_matrix = self.mesh_store.initial_pose
        if self.mesh_store.mirror_x: transformation_matrix = np.array([[-1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]) @ transformation_matrix
        if self.mesh_store.mirror_y: transformation_matrix = np.array([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]) @ transformation_matrix
        self.add_mesh(self.mesh_store.meshdict[self.mesh_store.reference], transformation_matrix)
        self.mesh_store.undo_poses.clear()
        self.output_text.append(f"-> Mirrored transformation matrix is: \n{transformation_matrix}")
        self.output_text.append(f"\n************************************************************\n")

    def add_mesh(self, mesh_source, transformation_matrix=None):
        """ add a mesh to the pyqt frame """
        source_verts, source_faces = self.mesh_store.add_mesh(mesh_source)
        if self.mesh_store.mesh_info:
            mesh = self.plotter.add_mesh(self.mesh_store.mesh_info, color=self.mesh_store.mesh_colors[self.mesh_store.mesh_name], opacity=self.mesh_store.mesh_opacity[self.mesh_store.mesh_name], name=self.mesh_store.mesh_name)
            mesh.user_matrix = self.mesh_store.transformation_matrix if transformation_matrix is None else transformation_matrix
            actor, _ = self.plotter.add_actor(mesh, pickable=True, name=self.mesh_store.mesh_name)

            actor_vertices, actor_faces = utils.get_mesh_actor_vertices_faces(actor)
            assert (actor_vertices == source_verts).all(), "vertices should be the same"
            assert (actor_faces == source_faces).all(), "faces should be the same"
            assert actor.name == self.mesh_store.mesh_name, "actor's name should equal to mesh_name"
            
            self.mesh_store.mesh_actors[self.mesh_store.mesh_name] = actor
            self.color_button.setText(self.mesh_store.mesh_colors[self.mesh_store.mesh_name])

            # add remove current mesh to removeMenu
            if self.mesh_store.mesh_name not in self.track_actors_names:
                self.track_actors_names.append(self.mesh_store.mesh_name)
                self.add_button_actor_name(self.mesh_store.mesh_name)
            #* very important for mirroring
            self.check_button(actor_name=self.mesh_store.mesh_name, output_text=False) 
        else:
            QtWidgets.QMessageBox.warning(QtWidgets.QMainWindow(), 'vision6D', "The mesh format is not supported!", QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
    
    def set_spacing(self):
        checked_button = self.button_group_actors_names.checkedButton()
        if checked_button:
            actor_name = checked_button.text()
            if actor_name in self.mesh_store.mesh_actors:
                spacing, ok = QtWidgets.QInputDialog().getText(QtWidgets.QMainWindow(), 'Input', "Set Spacing", text=str(self.mesh_store.mesh_spacing))
                if ok:
                    try: self.mesh_store.mesh_spacing = ast.literal_eval(spacing)
                    except: QtWidgets.QMessageBox.warning(QtWidgets.QMainWindow(), 'vision6D', "Format is not correct", QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
                    self.add_mesh(self.mesh_store.meshdict[actor_name])
            else:
                QtWidgets.QMessageBox.warning(QtWidgets.QMainWindow(), 'vision6D', "Need to select a mesh object instead", QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
        else:
            QtWidgets.QMessageBox.warning(QtWidgets.QMainWindow(), 'vision6D', "Need to select a mesh actor first", QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)

    def set_scalar(self, nocs, actor_name):
        mesh_data, colors = self.mesh_store.set_scalar(nocs, actor_name)
        if mesh_data:
            mesh = self.plotter.add_mesh(mesh_data, scalars=colors, rgb=True, opacity=self.mesh_store.mesh_opacity[actor_name], name=actor_name)
            transformation_matrix = pv.array_from_vtkmatrix(self.mesh_store.mesh_actors[actor_name].GetMatrix())
            mesh.user_matrix = transformation_matrix
            actor, _ = self.plotter.add_actor(mesh, pickable=True, name=actor_name)
            actor_colors = utils.get_mesh_actor_scalars(actor)
            assert (actor_colors == colors).all(), "actor_colors should be the same as colors"
            assert actor.name == actor_name, "actor's name should equal to actor_name"
            self.mesh_store.mesh_actors[actor_name] = actor
        else:
            QtWidgets.QMessageBox.warning(QtWidgets.QMainWindow(), 'vision6D', "Cannot set the selected color", QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)

    def set_color(self, color, actor_name):
        vertices, faces = utils.get_mesh_actor_vertices_faces(self.mesh_store.mesh_actors[actor_name])
        mesh_data = pv.wrap(trimesh.Trimesh(vertices, faces, process=False))
        mesh = self.plotter.add_mesh(mesh_data, color=color, opacity=self.mesh_store.mesh_opacity[actor_name], name=actor_name)
        transformation_matrix = pv.array_from_vtkmatrix(self.mesh_store.mesh_actors[actor_name].GetMatrix())
        mesh.user_matrix = transformation_matrix
        actor, _ = self.plotter.add_actor(mesh, pickable=True, name=actor_name)
        assert actor.name == actor_name, "actor's name should equal to actor_name"
        self.mesh_store.mesh_actors[actor_name] = actor

    def set_mesh_opacity(self, name: str, surface_opacity: float):
        self.mesh_store.mesh_opacity[name] = surface_opacity
        self.mesh_store.mesh_actors[name].user_matrix = pv.array_from_vtkmatrix(self.mesh_store.mesh_actors[name].GetMatrix())
        self.mesh_store.mesh_actors[name].GetProperty().opacity = surface_opacity
        self.plotter.add_actor(self.mesh_store.mesh_actors[name], pickable=True, name=name)

    def toggle_surface_opacity(self, up):
        checked_button = self.button_group_actors_names.checkedButton()
        if checked_button:
            if checked_button.text() in self.mesh_store.mesh_actors: 
                change = 0.05
                if not up: change *= -1
                current_opacity = self.opacity_spinbox.value()
                current_opacity += change
                current_opacity = np.clip(current_opacity, 0, 1)
                self.opacity_spinbox.setValue(current_opacity)
            
    def toggle_hide_meshes_button(self):
        self.toggle_hide_meshes_flag = not self.toggle_hide_meshes_flag
        if self.toggle_hide_meshes_flag:

            checked_button = self.button_group_actors_names.checkedButton()
            if checked_button: self.checked_button_name = checked_button.text()
            else: self.checked_button_name = None

            for button in self.button_group_actors_names.buttons():
                actor_name = button.text()
                if actor_name in self.mesh_store.mesh_actors:
                    if len(self.mesh_store.mesh_actors) != 1 and actor_name == self.checked_button_name: 
                        continue
                    self.ignore_opacity_change = True
                    self.opacity_spinbox.setValue(0)
                    self.ignore_opacity_change = False
                    self.mesh_store.store_mesh_opacity[actor_name] = copy.deepcopy(self.mesh_store.mesh_opacity[actor_name])
                    self.mesh_store.mesh_opacity[actor_name] = 0
                    self.set_mesh_opacity(actor_name, self.mesh_store.mesh_opacity[actor_name])
        else:
            for button in self.button_group_actors_names.buttons():
                actor_name = button.text()
                if actor_name in self.mesh_store.mesh_actors:
                    if len(self.mesh_store.mesh_actors) != 1 and actor_name == self.checked_button_name: 
                        continue
                    self.ignore_opacity_change = True
                    self.opacity_spinbox.setValue(self.mesh_store.store_mesh_opacity[actor_name])
                    self.ignore_opacity_change = False
                    self.set_mesh_opacity(actor_name, self.mesh_store.store_mesh_opacity[actor_name])
                    self.mesh_store.store_mesh_opacity[actor_name] = copy.deepcopy(self.mesh_store.mesh_opacity[actor_name])
                            
    def add_pose_file(self, pose_path):
        if pose_path:
            self.hintLabel.hide()
            self.mesh_store.pose_path = pose_path
            transformation_matrix = np.load(self.mesh_store.pose_path)
            self.mesh_store.transformation_matrix = transformation_matrix
            if self.mesh_store.mirror_x: transformation_matrix = np.array([[-1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]) @ transformation_matrix
            if self.mesh_store.mirror_y: transformation_matrix = np.array([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]) @ transformation_matrix
            self.add_pose(matrix=transformation_matrix)

    def add_pose(self, matrix:np.ndarray=None, rot:np.ndarray=None, trans:np.ndarray=None):
        if matrix is not None: 
            self.mesh_store.initial_pose = matrix
            self.reset_gt_pose()
        else:
            if (rot and trans): matrix = np.vstack((np.hstack((rot, trans)), [0, 0, 0, 1]))
        self.reset_camera()

    def set_pose(self):
        # get the gt pose
        get_text_dialog = GetTextDialog()
        res = get_text_dialog.exec_()
        if res == QtWidgets.QDialog.Accepted:
            try:
                gt_pose = ast.literal_eval(get_text_dialog.user_text)
                gt_pose = np.array(gt_pose)
                if gt_pose.shape == (4, 4):
                    self.hintLabel.hide()
                    transformation_matrix = gt_pose
                    self.mesh_store.transformation_matrix = transformation_matrix
                    if self.mesh_store.mirror_x: transformation_matrix = np.array([[-1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]) @ transformation_matrix
                    if self.mesh_store.mirror_y: transformation_matrix = np.array([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]) @ transformation_matrix
                    self.add_pose(matrix=transformation_matrix)
                else:
                    QtWidgets.QMessageBox.warning(QtWidgets.QMainWindow(), 'vision6D', "It needs to be a 4 by 4 matrix", QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok) 
            except: 
                QtWidgets.QMessageBox.warning(QtWidgets.QMainWindow(), 'vision6D', "Format is not correct", QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
    
    def reset_gt_pose(self):
        if self.mesh_store.initial_pose is not None:
            self.output_text.append(f"-> Reset the GT pose to: \n{self.mesh_store.initial_pose}")
            self.output_text.append(f"\n************************************************************\n")
            self.register_pose(self.mesh_store.initial_pose)

    def update_gt_pose(self):
        if self.mesh_store.initial_pose is not None:
            self.mesh_store.initial_pose = self.mesh_store.transformation_matrix
            self.current_pose()
            self.output_text.append(f"-> Update the GT pose to: \n{self.mesh_store.initial_pose}")
            self.output_text.append(f"\n************************************************************\n")

    def undo_pose(self):
        if self.button_group_actors_names.checkedButton():
            actor_name = self.button_group_actors_names.checkedButton().text()
            if self.mesh_store.undo_poses and len(self.mesh_store.undo_poses[actor_name]) != 0: 
                self.mesh_store.undo_pose(actor_name)
                # register the rest meshes' pose to current undoed pose
                self.check_button(actor_name=actor_name)
        else:
            QtWidgets.QMessageBox.warning(QtWidgets.QMainWindow(), 'vision6D', "Choose a mesh actor first", QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)

    def export_pose(self):
        if self.mesh_store.reference: 
            self.update_gt_pose()
            output_path, _ = QtWidgets.QFileDialog.getSaveFileName(QtWidgets.QMainWindow(), "Save File", "", "Pose Files (*.npy)")
            if output_path:
                if pathlib.Path(output_path).suffix == '': output_path = output_path.parent / (output_path.stem + '.npy')
                np.save(output_path, self.mesh_store.transformation_matrix)
                self.output_text.append(f"-> Saved:\n{self.mesh_store.transformation_matrix}\nExport to:\n {str(output_path)}")
                self.output_text.append(f"\n************************************************************\n")
        else:
            QtWidgets.QMessageBox.warning(QtWidgets.QMainWindow(), 'vision6D', "Need to set a reference or load a mesh first", QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
    
    def export_mesh_render(self, save_render=True):
        image = None
        if self.mesh_store.reference:
            image = self.mesh_store.render_mesh(camera=self.plotter.camera.copy())
            if save_render:
                output_path, _ = QtWidgets.QFileDialog.getSaveFileName(QtWidgets.QMainWindow(), "Save File", "", "Mesh Files (*.png)")
                if output_path:
                    if pathlib.Path(output_path).suffix == '': output_path = output_path.parent / (output_path.stem + '.png')
                    rendered_image = PIL.Image.fromarray(image)
                    rendered_image.save(output_path)
                    self.output_text.append(f"-> Export mesh render to:\n {str(output_path)}")
                    self.output_text.append(f"\n************************************************************\n")
        else:
            QtWidgets.QMessageBox.warning(QtWidgets.QMainWindow(), 'vision6D', "Need to load a mesh first", QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
        return image

    def export_segmesh_render(self):
        if self.mesh_store.reference and self.mask_store.mask_actor:
            mask_surface = self.mask_store.update_mask()
            mask_mesh = self.plotter.add_mesh(mask_surface, color="white", style='surface', opacity=self.mask_store.mask_opacity)
            actor, _ = self.plotter.add_actor(mask_mesh, pickable=True, name='mask')
            self.mask_store.mask_actor = actor
            segmask = self.mask_store.render_mask(camera=self.plotter.camera.copy())
            if np.max(segmask) > 1: segmask = segmask / 255
            image = self.mesh_store.render_mesh(camera=self.plotter.camera.copy())
            image = (image * segmask).astype(np.uint8)
            output_path, _ = QtWidgets.QFileDialog.getSaveFileName(QtWidgets.QMainWindow(), "Save File", "", "SegMesh Files (*.png)")
            if output_path:
                if pathlib.Path(output_path).suffix == '': output_path = output_path.parent / (output_path.stem + '.png')
                rendered_image = PIL.Image.fromarray(image)
                rendered_image.save(output_path)
                self.output_text.append(f"-> Export segmask render:\n to {str(output_path)}")
                self.output_text.append(f"\n************************************************************\n")
        else:
            QtWidgets.QMessageBox.warning(QtWidgets.QMainWindow(), 'vision6D', "Need to load a mesh or mask first", QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
            return 0
