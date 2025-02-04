'''
@author: Yike (Nicole) Zhang
@license: (C) Copyright.
@contact: yike.zhang@vanderbilt.edu
@software: Vision6D
@file: mainwindow.py
@time: 2023-07-03 20:33
@desc: the mainwindow to run application
'''

# General import
import os
os.environ["QT_API"] = "pyqt5" # Setting the Qt bindings for QtPy
import json
import copy
import functools

import PIL.Image
import numpy as np

# Qt5 import
from PyQt5 import QtWidgets, QtGui
from pyvistaqt import MainWindow
from PyQt5.QtCore import Qt, QPoint

# self defined package import
from .widgets import CustomQtInteractor
from .widgets import PopUpDialog

from .components import ImageStore
from .components import MaskStore
from .components import CameraStore
from .components import MeshStore
from .components import PointStore
from .components import VideoStore
from .components import FolderStore

from .containers import CameraContainer
from .containers import ImageContainer
from .containers import MaskContainer
from .containers import MeshContainer
from .containers import PointContainer
from .containers import PnPContainer
from .containers import VideoFolderContainer

np.set_printoptions(suppress=True)

class MyMainWindow(MainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        
        # Set up the main window layout
        self.setWindowTitle("Vision6D")
        self.window_size = (1920, 1080)
        self.main_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.main_widget)
        self.setAcceptDrops(True)

        # Initialize
        self.workspace_path = ''
        self.track_actors_names = []
        self.button_group_actors_names = QtWidgets.QButtonGroup(self)

        self.image_store = ImageStore()
        self.mask_store = MaskStore()
        self.camera_store = CameraStore(self.window_size)
        self.mesh_store = MeshStore(self.window_size)
        self.point_store = PointStore()
        self.video_store = VideoStore()
        self.folder_store = FolderStore()

        # Create widgets
        self.color_button = QtWidgets.QPushButton("Color")
        self.color_button.clicked.connect(self.show_color_popup)
        self.play_video_button = QtWidgets.QPushButton("Play Video")
        self.sample_video_button = QtWidgets.QPushButton("Sample Video")
        self.opacity_spinbox = QtWidgets.QDoubleSpinBox()
        self.opacity_spinbox.setMinimum(0.0)
        self.opacity_spinbox.setMaximum(1.0)
        self.opacity_spinbox.setDecimals(2)
        self.opacity_spinbox.setSingleStep(0.05)
        self.opacity_spinbox.setValue(0.3)
        self.opacity_spinbox.valueChanged.connect(self.opacity_value_change)
        self.output_text = QtWidgets.QTextEdit()
        self.output_text.setReadOnly(True)

        # Create the plotter
        self.create_plotter()

        # Add a QLabel as an overlay hint label
        self.hintLabel = QtWidgets.QLabel(self.plotter)
        self.hintLabel.setText("Drag and drop a file here...")
        self.hintLabel.setStyleSheet("""
                                    color: white; 
                                    background-color: rgba(0, 0, 0, 127); 
                                    padding: 10px;
                                    border: 2px dashed gray;
                                    """)
        self.hintLabel.setAlignment(Qt.AlignCenter)

        # create containers
        self.initial_containers()
                
        # Set bars
        self.set_panel_bar()
        self.set_menu_bars()

        # Set up the main layout with the left panel and the render window using QSplitter
        self.main_layout = QtWidgets.QHBoxLayout(self.main_widget)
        self.splitter = QtWidgets.QSplitter()
        self.splitter.addWidget(self.panel_widget)
        self.splitter.addWidget(self.plotter)
        self.splitter.setStretchFactor(0, 1) # for self.panel_widget
        self.splitter.setStretchFactor(1, 3) # for self.plotter

        self.main_layout.addWidget(self.splitter)

        # Show the plotter
        self.show_plot()

        # Shortcut key bindings
        self.key_bindings()

    def initial_containers(self):
        self.camera_container = CameraContainer(plotter=self.plotter)
        self.camera_container.set_camera_props()
        
        self.image_container = ImageContainer(plotter=self.plotter, 
                                            hintLabel=self.hintLabel, 
                                            track_actors_names=self.track_actors_names, 
                                            add_button_actor_name=self.add_button_actor_name, 
                                            check_button=self.check_button,
                                            output_text=self.output_text)
        
        self.mask_container = MaskContainer(plotter=self.plotter,
                                            hintLabel=self.hintLabel, 
                                            track_actors_names=self.track_actors_names, 
                                            add_button_actor_name=self.add_button_actor_name, 
                                            check_button=self.check_button, 
                                            output_text=self.output_text)
        
        self.point_container = PointContainer(plotter=self.plotter,
                                            hintLabel=self.hintLabel,
                                            track_actors_names=self.track_actors_names, 
                                            add_button_actor_name=self.add_button_actor_name,
                                            output_text=self.output_text,
                                            )
        
        self.mesh_container = MeshContainer(color_button=self.color_button,
                                            plotter=self.plotter,
                                            hintLabel=self.hintLabel,
                                            track_actors_names=self.track_actors_names,
                                            add_button_actor_name=self.add_button_actor_name,
                                            button_group_actors_names=self.button_group_actors_names,
                                            check_button=self.check_button,
                                            opacity_spinbox=self.opacity_spinbox,
                                            opacity_value_change=self.opacity_value_change,
                                            reset_camera=self.camera_container.reset_camera,
                                            current_pose=self.current_pose,
                                            register_pose=self.register_pose,
                                            output_text=self.output_text)
        
        self.pnp_container = PnPContainer(plotter=self.plotter,
                                        export_mesh_render=self.mesh_container.export_mesh_render,
                                        output_text=self.output_text)
        
        self.video_folder_container = VideoFolderContainer(play_video_button=self.play_video_button, 
                                                        sample_video_button=self.sample_video_button, 
                                                        hintLabel=self.hintLabel, 
                                                        register_pose=self.register_pose,
                                                        current_pose=self.current_pose,
                                                        add_image=self.image_container.add_image,
                                                        add_folder=self.add_folder,
                                                        clear_plot=self.clear_plot,
                                                        output_text=self.output_text)

    def key_bindings(self):
        # Camera related key bindings
        QtWidgets.QShortcut(QtGui.QKeySequence("c"), self).activated.connect(self.camera_container.reset_camera)
        QtWidgets.QShortcut(QtGui.QKeySequence("z"), self).activated.connect(self.camera_container.zoom_out)
        QtWidgets.QShortcut(QtGui.QKeySequence("x"), self).activated.connect(self.camera_container.zoom_in)

        # Mirror related key bindings
        QtWidgets.QShortcut(QtGui.QKeySequence("o"), self).activated.connect(lambda direction='x': self.mirror_actors(direction))
        QtWidgets.QShortcut(QtGui.QKeySequence("p"), self).activated.connect(lambda direction='y': self.mirror_actors(direction))
        
        # Image related key bindings
        QtWidgets.QShortcut(QtGui.QKeySequence("b"), self).activated.connect(lambda up=True: self.image_container.toggle_image_opacity(up))
        QtWidgets.QShortcut(QtGui.QKeySequence("n"), self).activated.connect(lambda up=False: self.image_container.toggle_image_opacity(up))

        # Mask related key bindings
        QtWidgets.QShortcut(QtGui.QKeySequence("t"), self).activated.connect(self.mask_container.reset_mask)
        QtWidgets.QShortcut(QtGui.QKeySequence("g"), self).activated.connect(lambda up=True: self.mask_container.toggle_mask_opacity(up))
        QtWidgets.QShortcut(QtGui.QKeySequence("h"), self).activated.connect(lambda up=False: self.mask_container.toggle_mask_opacity(up))

        # Mesh related key bindings 
        QtWidgets.QShortcut(QtGui.QKeySequence("k"), self).activated.connect(self.mesh_container.reset_gt_pose)
        QtWidgets.QShortcut(QtGui.QKeySequence("l"), self).activated.connect(self.mesh_container.update_gt_pose)
        QtWidgets.QShortcut(QtGui.QKeySequence("s"), self).activated.connect(self.mesh_container.undo_pose)
        QtWidgets.QShortcut(QtGui.QKeySequence("y"), self).activated.connect(lambda up=True: self.mesh_container.toggle_surface_opacity(up))
        QtWidgets.QShortcut(QtGui.QKeySequence("u"), self).activated.connect(lambda up=False: self.mesh_container.toggle_surface_opacity(up))

        # Video Folder related key bindings 
        QtWidgets.QShortcut(QtGui.QKeySequence("Right"), self).activated.connect(self.video_folder_container.next_frame)
        QtWidgets.QShortcut(QtGui.QKeySequence("Left"), self).activated.connect(self.video_folder_container.prev_frame)
        QtWidgets.QShortcut(QtGui.QKeySequence("Space"), self).activated.connect(self.video_folder_container.play_video)

    def showMaximized(self):
        super(MyMainWindow, self).showMaximized()

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.accept()
            self.hintLabel.hide()  # Hide hint when dragging
        else:
            e.ignore()

    def dropEvent(self, e):
        for url in e.mimeData().urls():
            file_path = url.toLocalFile()
            if os.path.isdir(file_path): self.add_folder(folder_path=file_path)
            else:
                # Load workspace json file
                if file_path.endswith(('.json')): self.add_workspace(workspace_path=file_path)
                # Load mesh file
                elif file_path.endswith(('.mesh', '.ply', '.stl', '.obj', '.off', '.dae', '.fbx', '.3ds', '.x3d')):
                    self.mesh_container.add_mesh_file(mesh_path=file_path)
                # Load video file
                elif file_path.endswith(('.avi', '.mp4', '.mkv', '.mov', '.fly', '.wmv', '.mpeg', '.asf', '.webm')):
                    self.video_folder_container.add_video_file(video_path=file_path)
                # Load image/mask file
                elif file_path.endswith(('.png', '.jpg', 'jpeg', '.tiff', '.bmp', '.webp', '.ico')):  # add image/mask
                    file_data = np.array(PIL.Image.open(file_path).convert('L'), dtype='uint8')
                    unique, _ = np.unique(file_data, return_counts=True)
                    if len(unique) == 2: self.mask_container.add_mask_file(mask_path=file_path)
                    else: self.image_container.add_image_file(image_path=file_path) 
                        
                elif file_path.endswith('.npy'): self.mesh_container.add_pose_file(pose_path=file_path)
                else:
                    QtWidgets.QMessageBox.warning(self, 'vision6D', "File format is not supported!", QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
                    return 0

    def resizeEvent(self, e):
        x = (self.plotter.size().width() - self.hintLabel.width()) // 2
        y = (self.plotter.size().height() - self.hintLabel.height()) // 2
        self.hintLabel.move(x, y)
        super().resizeEvent(e)

    # ^Menu
    def set_menu_bars(self):
        mainMenu = self.menuBar()
        
        # allow to add files
        fileMenu = mainMenu.addMenu('File')
        fileMenu.addAction('Add Workspace', functools.partial(self.add_workspace, prompt=True))
        fileMenu.addAction('Add Folder', functools.partial(self.add_folder, prompt=True))
        fileMenu.addAction('Add Video', functools.partial(self.video_folder_container.add_video_file, prompt=True))
        fileMenu.addAction('Add Image', functools.partial(self.image_container.add_image_file, prompt=True))
        fileMenu.addAction('Add Mask', functools.partial(self.mask_container.add_mask_file, prompt=True))
        fileMenu.addAction('Add Mesh', functools.partial(self.mesh_container.add_mesh_file, prompt=True))
        fileMenu.addAction('Add Points', functools.partial(self.point_container.load_points_file, prompt=True))
        fileMenu.addAction('Draw Mask', self.mask_container.draw_mask)
        fileMenu.addAction('Clear', self.clear_plot)

        # allow to export files
        exportMenu = mainMenu.addMenu('Export')
        exportMenu.addAction('Image', self.image_container.export_image)
        exportMenu.addAction('Mask', self.mask_container.export_mask)
        exportMenu.addAction('Pose', self.mesh_container.export_pose)
        exportMenu.addAction('Mesh Render', self.mesh_container.export_mesh_render)
        exportMenu.addAction('SegMesh Render', self.mesh_container.export_segmesh_render)
        
        # Add video related actions
        VideoFolderMenu = mainMenu.addMenu('Video/Folder')
        VideoFolderMenu.addAction('Play', self.video_folder_container.play_video)
        VideoFolderMenu.addAction('Sample', self.video_folder_container.sample_video)
        VideoFolderMenu.addAction('Save Frame', self.video_folder_container.save_frame)
        VideoFolderMenu.addAction('Prev Frame', self.video_folder_container.prev_frame)
        VideoFolderMenu.addAction('Next Frame', self.video_folder_container.next_frame)

        # Add camera related actions
        CameraMenu = mainMenu.addMenu('Camera')
        CameraMenu.addAction('Calibrate', self.camera_container.camera_calibrate)
        CameraMenu.addAction('Reset Camera (d)', self.camera_container.reset_camera)
        CameraMenu.addAction('Zoom In (x)', self.camera_container.zoom_in)
        CameraMenu.addAction('Zoom Out (z)', self.camera_container.zoom_out)
        
        # Add register related actions
        RegisterMenu = mainMenu.addMenu('Register')
        RegisterMenu.addAction('Reset GT Pose (k)', self.mesh_container.reset_gt_pose)
        RegisterMenu.addAction('Reset Mask (t)', self.mask_container.reset_mask)
        RegisterMenu.addAction('Update GT Pose (l)', self.mesh_container.update_gt_pose)
        RegisterMenu.addAction('Undo Pose (s)', self.mesh_container.undo_pose)

        # Add pnp algorithm related actions
        PnPMenu = mainMenu.addMenu('PnP')
        PnPMenu.addAction('EPnP with mesh', self.pnp_container.epnp_mesh)
        PnPMenu.addAction('EPnP with nocs mask', functools.partial(self.pnp_container.epnp_mask, True))
        PnPMenu.addAction('EPnP with latlon mask', functools.partial(self.pnp_container.epnp_mask, False))

    # ^Panel
    def set_panel_bar(self):
        # Create a left panel layout
        self.panel_widget = QtWidgets.QWidget()
        self.panel_layout = QtWidgets.QVBoxLayout(self.panel_widget)

        # Create a top panel bar with a toggle button
        self.panel_bar = QtWidgets.QMenuBar()
        self.toggle_action = QtWidgets.QAction("Panel", self)
        self.toggle_action.triggered.connect(self.toggle_panel)
        self.panel_bar.addAction(self.toggle_action)
        self.setMenuBar(self.panel_bar)

        self.panel_display()
        self.panel_output()
        
        # Set the stretch factor for each section to be equal
        self.panel_layout.setStretchFactor(self.display, 1)
        self.panel_layout.setStretchFactor(self.output, 1)

    def toggle_panel(self):
        if self.panel_widget.isVisible():
            # self.panel_widget width changes when the panel is visiable or hiden
            self.panel_widget_width = self.panel_widget.width()
            self.panel_widget.hide()
            x = (self.plotter.size().width() + self.panel_widget_width - self.hintLabel.width()) // 2
            y = (self.plotter.size().height() - self.hintLabel.height()) // 2
            self.hintLabel.move(x, y)
        else:
            self.panel_widget.show()
            x = (self.plotter.size().width() - self.panel_widget_width - self.hintLabel.width()) // 2
            y = (self.plotter.size().height() - self.hintLabel.height()) // 2
            self.hintLabel.move(x, y)
        
    #^ Panel Display
    def panel_display(self):
        self.display = QtWidgets.QGroupBox("Console")
        display_layout = QtWidgets.QVBoxLayout()
        display_layout.setContentsMargins(10, 15, 10, 5)

        #* Create the top widgets (layout)
        top_layout = QtWidgets.QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)

        # Create Grid layout for function buttons
        top_grid_layout = QtWidgets.QGridLayout()

        # Create the set camera button
        set_camera_button = QtWidgets.QPushButton("Set Camera")
        set_camera_button.clicked.connect(self.camera_container.set_camera)
        top_grid_layout.addWidget(set_camera_button, 0, 0)

        # Create the actor pose button
        actor_pose_button = QtWidgets.QPushButton("Set Pose")
        actor_pose_button.clicked.connect(self.mesh_container.set_pose)
        top_grid_layout.addWidget(actor_pose_button, 0, 1)

        # Create the draw mask button
        draw_mask_button = QtWidgets.QPushButton("Draw Mask")
        draw_mask_button.clicked.connect(self.mask_container.draw_mask)
        top_grid_layout.addWidget(draw_mask_button, 0, 2)

        # Create the video related button
        self.play_video_button.clicked.connect(self.video_folder_container.play_video)
        top_grid_layout.addWidget(self.play_video_button, 0, 3)

        self.sample_video_button.clicked.connect(self.video_folder_container.sample_video)
        top_grid_layout.addWidget(self.sample_video_button, 1, 0)

        self.save_frame_button = QtWidgets.QPushButton("Save Frame")
        self.save_frame_button.clicked.connect(self.video_folder_container.save_frame)
        top_grid_layout.addWidget(self.save_frame_button, 1, 1)

        self.prev_frame_button = QtWidgets.QPushButton("Prev Frame")
        self.prev_frame_button.clicked.connect(self.video_folder_container.prev_frame)
        top_grid_layout.addWidget(self.prev_frame_button, 1, 2)

        self.next_frame_button = QtWidgets.QPushButton("Next Frame")
        self.next_frame_button.clicked.connect(self.video_folder_container.next_frame)
        top_grid_layout.addWidget(self.next_frame_button, 1, 3)

        top_grid_widget = QtWidgets.QWidget()
        top_grid_widget.setLayout(top_grid_layout)
        top_layout.addWidget(top_grid_widget)
        display_layout.addLayout(top_layout)

        #* Create the bottom widgets
        actor_widget = QtWidgets.QLabel("Actors")
        display_layout.addWidget(actor_widget)

        actor_grid_layout = QtWidgets.QGridLayout()
        actor_grid_layout.setContentsMargins(10, 5, 10, 10)

        # Create the color dropdown menu
        actor_grid_layout.addWidget(self.color_button, 0, 0)
        
        actor_grid_layout.addWidget(self.opacity_spinbox, 0, 1)

        # Create the hide button
        hide_button = QtWidgets.QPushButton("Toggle Meshes")
        hide_button.clicked.connect(self.mesh_container.toggle_hide_meshes_button)
        actor_grid_layout.addWidget(hide_button, 0, 2)

        # Create the remove button
        remove_button = QtWidgets.QPushButton("Remove Actor")
        remove_button.clicked.connect(self.remove_actors_button)
        actor_grid_layout.addWidget(remove_button, 0, 3)
        display_layout.addLayout(actor_grid_layout)

        # Create the spacing button
        self.spacing_button = QtWidgets.QPushButton("Spacing")
        self.spacing_button.clicked.connect(self.mesh_container.set_spacing)
        actor_grid_layout.addWidget(self.spacing_button, 1, 0)

        # Create the mirror x button
        self.mirror_x_button = QtWidgets.QPushButton("Mirror X")
        self.mirror_x_button.clicked.connect(lambda _, direction="x": self.mirror_actors(direction))
        actor_grid_layout.addWidget(self.mirror_x_button, 1, 1)

        # Create the mirror y button
        self.mirror_y_button = QtWidgets.QPushButton("Mirror Y")
        self.mirror_y_button.clicked.connect(lambda _, direction="y": self.mirror_actors(direction))
        actor_grid_layout.addWidget(self.mirror_y_button, 1, 2)

        # Create a scroll area for the buttons
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        display_layout.addWidget(scroll_area)

        # Create a container widget for the buttons
        button_container = QtWidgets.QWidget()
        self.button_layout = QtWidgets.QVBoxLayout()
        self.button_layout.setSpacing(0)  # Remove spacing between buttons
        button_container.setLayout(self.button_layout)

        self.button_layout.addStretch()

        # Set the container widget as the scroll area's widget
        scroll_area.setWidget(button_container)

        self.display.setLayout(display_layout)
        self.panel_layout.addWidget(self.display)

    #^ Panel Output
    def panel_output(self):
        # Add a spacer to the top of the main layout
        self.output = QtWidgets.QGroupBox("Output")
        output_layout = QtWidgets.QVBoxLayout()
        output_layout.setContentsMargins(10, 15, 10, 5)

        #* Create the top widgets (layout)
        top_layout = QtWidgets.QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)

        # Create Grid layout for function buttons
        grid_layout = QtWidgets.QGridLayout()

        # Create the set camera button
        copy_text_button = QtWidgets.QPushButton("Copy")
        copy_text_button.clicked.connect(self.copy_output_text)
        grid_layout.addWidget(copy_text_button, 0, 2, 1, 1)

        # Create the actor pose button
        clear_text_button = QtWidgets.QPushButton("Clear")
        clear_text_button.clicked.connect(self.clear_output_text)
        grid_layout.addWidget(clear_text_button, 0, 3, 1, 1)

        grid_widget = QtWidgets.QWidget()
        grid_widget.setLayout(grid_layout)
        top_layout.addWidget(grid_widget)
        output_layout.addLayout(top_layout)

        # Access to the system clipboard
        self.clipboard = QtGui.QGuiApplication.clipboard()
        output_layout.addWidget(self.output_text)
        self.output.setLayout(output_layout)
        self.panel_layout.addWidget(self.output)

    #^ Plotter
    def create_plotter(self):
        self.frame = QtWidgets.QFrame()
        self.frame.setFixedSize(*self.window_size)
        self.plotter = CustomQtInteractor(self.frame, self)
        # self.plotter.setFixedSize(*self.window_size)
        self.signal_close.connect(self.plotter.close)

    def show_plot(self):
        self.plotter.enable_joystick_actor_style()
        self.plotter.enable_trackball_actor_style()
        
        self.plotter.add_axes()
        self.plotter.add_camera_orientation_widget()
        self.plotter.background_color = "black"

        self.plotter.show()
        self.show()
   
    def register_pose(self, pose):
        for actor_name, actor in self.mesh_store.mesh_actors.items():
            actor.user_matrix = pose
            self.plotter.add_actor(actor, pickable=True, name=actor_name)

    def current_pose(self, text=None, output_text=True):
        self.mesh_store.current_pose()
        if text and output_text: 
            self.output_text.append(f"--> Current <span style='background-color:yellow; color:black;'>{text}</span> pose is:")
            self.output_text.append(f"{self.mesh_store.transformation_matrix}")
            self.output_text.append(f"\n************************************************************\n")
        self.register_pose(self.mesh_store.transformation_matrix)

    def button_actor_name_clicked(self, text, output_text=True):
        if text in self.mesh_store.mesh_actors:
            self.color_button.setText(self.mesh_store.mesh_colors[text])
            self.mesh_store.reference = text
            self.current_pose(text=text, output_text=output_text)
            curr_opacity = self.mesh_store.mesh_actors[self.mesh_store.reference].GetProperty().opacity
            self.opacity_spinbox.setValue(curr_opacity)
        else:
            self.color_button.setText("Color")
            if text == 'image': curr_opacity = self.image_store.image_opacity
            elif text == 'mask': curr_opacity = self.mask_store.mask_opacity
            else: curr_opacity = self.opacity_spinbox.value()
            self.mesh_store.reference = None #* For fixing some bugs in segmesh render function
            self.opacity_spinbox.setValue(curr_opacity)
            
    def check_button(self, actor_name, output_text=True):
        for button in self.button_group_actors_names.buttons():
            if button.text() == actor_name: 
                button.setChecked(True)
                self.button_actor_name_clicked(text=actor_name, output_text=output_text)
                break     

    def add_button_actor_name(self, actor_name):
        button = QtWidgets.QPushButton(actor_name)
        button.setCheckable(True)  # Set the button to be checkable
        button.clicked.connect(lambda _, text=actor_name: self.button_actor_name_clicked(text))
        button.setChecked(True)
        button.setFixedSize(self.display.size().width(), 50)
        self.button_layout.insertWidget(0, button) # insert from the top # self.button_layout.addWidget(button)
        self.button_group_actors_names.addButton(button)
        self.button_actor_name_clicked(text=actor_name)
    
    def opacity_value_change(self, value):
        if self.mesh_container.ignore_opacity_change: return 0
        checked_button = self.button_group_actors_names.checkedButton()
        if checked_button:
            actor_name = checked_button.text()
            if actor_name == 'image': self.image_container.set_image_opacity(value)
            elif actor_name == 'mask': self.mask_container.set_mask_opacity(value)
            elif actor_name in self.mesh_store.mesh_actors:
                self.mesh_store.mesh_opacity[actor_name] = value
                self.mesh_store.store_mesh_opacity[actor_name] = copy.deepcopy(self.mesh_store.mesh_opacity[actor_name])
                self.mesh_container.set_mesh_opacity(actor_name, self.mesh_store.mesh_opacity[actor_name])
    
    def update_color_button_text(self, text, popup):
        self.color_button.setText(text)
        popup.close() # automatically close the popup window

    def show_color_popup(self):

        checked_button = self.button_group_actors_names.checkedButton()
        if checked_button:
            actor_name = checked_button.text()
            if actor_name in self.mesh_store.mesh_actors:
                popup = PopUpDialog(self, on_button_click=lambda text: self.update_color_button_text(text, popup))
                button_position = self.color_button.mapToGlobal(QPoint(0, 0))
                popup.move(button_position + QPoint(self.color_button.width(), 0))
                popup.exec_()

                text = self.color_button.text()
                self.mesh_store.mesh_colors[actor_name] = text
                if text == 'nocs': self.mesh_container.set_scalar(True, actor_name)
                elif text == 'latlon': self.mesh_container.set_scalar(False, actor_name)
                else: self.mesh_container.set_color(text, actor_name)
            else:
                QtWidgets.QMessageBox.warning(self, 'vision6D', "Only be able to color mesh actors", QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
        else:
            QtWidgets.QMessageBox.warning(self, 'vision6D', "Need to select an actor first", QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
 
    def copy_output_text(self):
        self.clipboard.setText(self.output_text.toPlainText())
        
    def clear_output_text(self):
        self.output_text.clear()

    def add_workspace(self, workspace_path='', prompt=False):
        if prompt:
            workspace_path, _ = QtWidgets.QFileDialog().getOpenFileName(None, "Open file", "", "Files (*.json)")
        if workspace_path:
            if self.workspace_path: self.clear_plot()
            self.workspace_path = workspace_path
            self.hintLabel.hide()
            with open(str(self.workspace_path), 'r') as f: workspace = json.load(f)
            if 'image_path' in workspace: self.image_container.add_image_file(image_path=workspace['image_path'])
            if 'video_path' in workspace: self.video_folder_container.add_video_file(video_path=workspace['video_path'])
            if 'mask_path' in workspace: self.mask_container.add_mask_file(mask_path=workspace['mask_path'])
            # need to load pose before loading meshes
            if 'pose_path' in workspace: self.mesh_container.add_pose_file(pose_path=workspace['pose_path'])
            if 'mesh_path' in workspace:
                mesh_paths = workspace['mesh_path']
                for path in mesh_paths: self.mesh_container.add_mesh_file(mesh_path=path)
            
            # reset camera
            self.camera_container.reset_camera()

    def add_folder(self, folder_path='', prompt=False):
        if prompt: 
            folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            if self.video_store.video_path or self.workspace_path: self.clear_plot() # main goal is to set video_path to None
            image_path, mask_path, pose_path, mesh_path = self.folder_store.add_folder(folder_path=folder_path)
            if image_path or mask_path or pose_path or mesh_path:
                if image_path: self.image_container.add_image_file(image_path=image_path)
                if mask_path: self.mask_container.add_mask_file(mask_path=mask_path)
                if pose_path: self.mesh_container.add_pose_file(pose_path=pose_path)
                if mesh_path: 
                    with open(mesh_path, 'r') as f: mesh_path = f.read().splitlines()
                    for path in mesh_path: self.mesh_container.add_mesh_file(path)
                self.play_video_button.setEnabled(False)
                self.sample_video_button.setEnabled(False)
                self.play_video_button.setText(f"Frame ({self.folder_store.current_frame}/{self.folder_store.total_frame})")
                self.camera_container.reset_camera()
            else:
                self.folder_store.reset()
                QtWidgets.QMessageBox.warning(self, 'vision6D', "Not a valid folder, please reload a folder", QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)

    def mirror_actors(self, direction):
        checked_button = self.button_group_actors_names.checkedButton()
        if checked_button:
            actor_name = checked_button.text()
            if actor_name == 'image':
                self.image_container.mirror_image(direction)
            elif actor_name == 'mask':
                self.mask_container.mirror_mask(direction)
            elif actor_name in self.mesh_store.mesh_actors:
                self.mesh_container.mirror_mesh(direction)
        else:
            QtWidgets.QMessageBox.warning(self, 'vision6D', "Need to select an actor first", QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)

    def remove_actor(self, button):
        name = button.text()
        if name == 'image': 
            actor = self.image_store.image_actor
            self.image_store.reset()
        elif name == 'mask':
            actor = self.mask_store.mask_actor
            self.mask_store.reset()
        elif name in self.mesh_store.mesh_actors: 
            actor = self.mesh_store.mesh_actors[name]
            self.mesh_store.remove_mesh(name)
            self.color_button.setText("Color")
        elif name in self.point_store.point_actors:
            actor = self.point_store.point_actors[name]
            self.point_store.remove_point(name)

        self.plotter.remove_actor(actor)
        self.track_actors_names.remove(name)
        # remove the button from the button group
        self.button_group_actors_names.removeButton(button)
        # remove the button from the self.button_layout widget
        self.button_layout.removeWidget(button)
        # offically delete the button
        button.deleteLater()

        # clear out the plot if there is no actor
        if (self.image_store.image_actor is None) and (self.mask_store.mask_actor is None) and (len(self.mesh_store.mesh_actors) == 0) and (len(self.point_store.point_actors) == 0): 
            self.clear_plot()

    def remove_actors_button(self):
        checked_button = self.button_group_actors_names.checkedButton()
        if checked_button: self.remove_actor(checked_button)
        else:
            QtWidgets.QMessageBox.warning(self, 'vision6D', "Need to select an actor first", QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
            return 0

    def clear_plot(self):
        # Clear out everything in the remove menu
        for button in self.button_group_actors_names.buttons():
            name = button.text()
            if name == 'image': 
                actor = self.image_store.image_actor
                self.image_store.reset()
                self.image_store.mirror_x = False
                self.image_store.mirror_y = False
            elif name == 'mask': 
                actor = self.mask_store.mask_actor
                self.mask_store.reset()
                self.mask_store.mirror_x = False
                self.mask_store.mirror_y = False
            elif name in self.mesh_store.mesh_actors: 
                actor = self.mesh_store.mesh_actors[name]
                self.mesh_store.remove_mesh(name)
                self.color_button.setText("Color")
            elif name in self.point_store.point_actors:
                actor = self.point_store.point_actors[name]
                self.point_store.remove_point(name)

            self.plotter.remove_actor(actor)
            # remove the button from the button group
            self.button_group_actors_names.removeButton(button)
            # remove the button from the self.button_layout widget
            self.button_layout.removeWidget(button)
            # offically delete the button
            button.deleteLater()

        self.mesh_store.reset()
        self.point_store.reset()
        self.video_store.reset()
        self.folder_store.reset()
        self.workspace_path = ''
        self.track_actors_names.clear()
        self.clear_output_text()

        self.color_button.setText("Color")
        self.play_video_button.setText("Play Video")
        self.opacity_spinbox.setValue(0.3)
        
        self.hintLabel.show()
