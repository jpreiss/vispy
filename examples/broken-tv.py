#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# VisPy - Copyright (c) 2013, Vispy Development Team
# All rights reserved.
# -----------------------------------------------------------------------------
""" 
Example demonstrating showing a, image with a fixed ratio.
"""

import time
import numpy as np

from transforms import ortho
from vispy import oogl
from vispy import app
from vispy import gl


# Image to be displayed
W,H = 64,48
I = np.random.uniform(0,1,(W,H)).astype(np.float32)

# A simple texture quad
data = np.zeros(4, dtype=[ ('a_position', np.float32, 2), 
                           ('a_texcoord', np.float32, 2) ])
data['a_position'] = np.array([[0, 0], [W, 0], [0, H], [W, H]])
data['a_texcoord'] = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])


VERT_SHADER = """
// Uniforms
uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;
uniform float u_antialias;

// Attributes
attribute vec2 a_position;
attribute vec2 a_texcoord;

// Varyings
varying vec2 v_texcoord;

// Main
void main (void)
{
    v_texcoord = a_texcoord;
    gl_Position = u_projection * u_view * u_model * vec4(a_position,0.0,1.0);
}
"""

FRAG_SHADER = """
uniform sampler2D u_texture;
varying vec2 v_texcoord;
void main()
{    
    gl_FragColor = texture2D(u_texture, v_texcoord);
    gl_FragColor.a = 1.0;
}

"""


class Canvas(app.Canvas):
    
    def __init__(self):
        app.Canvas.__init__(self)

        self.geometry = (0,0,W*5,H*5)

        self.program = oogl.ShaderProgram( oogl.VertexShader(VERT_SHADER), 
                                            oogl.FragmentShader(FRAG_SHADER) )
        self.texture = oogl.Texture2D(I)
        self.texture.set_filter(gl.GL_NEAREST, gl.GL_NEAREST)
        
        self.program.uniforms['u_texture'] = self.texture
        self.program.attributes['a_position'] = data['a_position']
        self.program.attributes['a_texcoord'] = data['a_texcoord']

        self.view = np.eye(4,dtype=np.float32)
        self.model = np.eye(4,dtype=np.float32)
        self.projection = np.eye(4,dtype=np.float32)

        self.program.uniforms['u_model'] = self.model
        self.program.uniforms['u_view'] = self.view
        self.projection = ortho(0, W, 0, H, -1, 1)
        self.program.uniforms['u_projection'] = self.projection
    
    def on_initialize(self, event):
        gl.glClearColor(1,1,1,1)
    
    def on_resize(self, event):
        width, height = event.size
        gl.glViewport(0, 0, width, height)
        self.projection = ortho( 0, width, 0, height, -100, 100 )
        self.program.uniforms['u_projection'] = self.projection

        # Compute thje new size of the quad 
        r = width/float(height)
        R = W/float(H)
        if r < R:
            w,h = width, width/R
            x,y = 0, int((height-h)/2)
        else:
            w,h = height*R, height
            x,y = int((width-w)/2), 0
        data['a_position'] = np.array([[x, y], [x+w, y], [x, y+h], [x+w, y+h]])
        self.program.attributes['a_position'] = data['a_position']

    
    def on_paint(self, event):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        with self.program as prog:
            I[...] = np.random.uniform(0,1,(W,H)).astype(np.float32)
            self.texture.set_data(I)
            prog.draw_arrays(gl.GL_TRIANGLE_STRIP)
        self.update()


if __name__ == '__main__':
    c = Canvas()
    c.show()
    app.run()
