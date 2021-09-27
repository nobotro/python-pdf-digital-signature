# -*- coding: utf-8 -*-
import Tkinter
import math
import multiprocessing
import threading
from Tkinter import *
import time
import base64
from io import BytesIO

from PIL import ImageTk
from pdfrw import PdfReader, PdfWriter, PageMerge
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

class Signature_Manager(object):


    def __init__(self):
        self.capture_finished_callback=None
        self.old_x=None
        self.old_y=None
        self.line_width=1

        self.loop_status=False

        #position of signature image in templete pdf,startpos is in bottom left corner
        self.signature_pos_x=100
        self.signature_pos_y=800

        #scaling of signature pdf
        self.scaling_x=0.24
        self.scaling_y=0.24
        self.localstatus=False
       #line color
        self.line_color='blue'
        self.master=None
        self.tkinter_signature_canvas=None

        self.biometric_data={'cordinates':[],'timestamps':[],'cordinates_start_pos':'topleftcorner'}
        self.singature_bytes = BytesIO()
        self.signature_canvas = canvas.Canvas(self.singature_bytes)

        #signature canvas configure
        self.signature_canvas.scale(self.scaling_x,self.scaling_y)
        self.signature_canvas.setLineCap(1)
        self.signature_canvas.setLineJoin(1)
        self.signature_canvas.setStrokeColor(self.line_color)
        self.pdf_to_sign=None
        self.bytes=None


    def sign_pdf(self,pdfbytes):




        self.pdf_to_sign=pdfbytes
        self.localstatus=True
        self.init_window_spec()
        self.windowloop()
        return self.bytes


    def reinit_global_var(self):


        self.old_x = None
        self.old_y = None

        self.biometric_data = {'cordinates': [], 'timestamps': [], 'cordinates_start_pos': 'topleftcorner'}

        self.singature_bytes = BytesIO()

        self.signature_canvas = canvas.Canvas(self.singature_bytes)
        self.signature_canvas.scale(self.scaling_x, self.scaling_y)
        self.signature_canvas.setLineCap(1)
        self.signature_canvas.setLineJoin(1)
        self.signature_canvas.setStrokeColor(self.line_color)



    def init_window_spec(self):

        self.master = Tk()




        # self.master.iconbitmap('sig.ico')
        self.master.title('ხელმოწერა')

        # windows size
        self.master.geometry('700x200')
        self.master.resizable(0, 0)
        self.tkinter_signature_canvas = Canvas(self.master)
        self.tkinter_signature_canvas.bind('<B1-Motion>', self.mouse_move)
        self.tkinter_signature_canvas.bind('<ButtonRelease-1>', self.mouse_up)
        self.tkinter_signature_canvas.bind('<ButtonPress-3>', self.sign)
        self.tkinter_signature_canvas.pack_propagate(0)
        self.tkinter_signature_canvas.pack(fill=BOTH, expand=True)

        # print(master.winfo_screenheight())
        # print(master.winfo_screenwidth())
        # master.wm_attributes("-fullscreen", True)








    def mouse_move(self,event):

        if self.old_x and self.old_y:



            #this code is used to define line width if required
            # distance = math.sqrt(((event.x - old_x) ** 2) + ((event.y - old_y) ** 2))
            # print (str(distance))
            # if distance>=40:
            #     line_width=0.4
            # else:
            #     line_width=0.7
            #


            #draw line to tkinter canvas and reportgen canvas

            self.signature_canvas.setLineWidth(self.line_width)
            self.signature_canvas.line(math.fabs(self.signature_pos_x+self.old_x), self.signature_pos_y+math.fabs(200-(self.old_y)), math.fabs(self.signature_pos_x+event.x), self.signature_pos_y+math.fabs(200-(event.y)))
            self.tkinter_signature_canvas.create_line(self.old_x, self.old_y, event.x, event.y, width=self.line_width+0.9, fill='#000F55',capstyle=ROUND, joinstyle=ROUND, smooth=True)

            #save bio metric data
            self.biometric_data['cordinates'].append([self.old_x,self.old_y])
            self. biometric_data['timestamps'].append(time.time())

        self.old_x = event.x
        self.old_y = event.y


    def mouse_up(self,event):

        self.old_x = None
        self.old_y = None


    def sign(self,event):





        #save signature biometric data in meta headers and draw signature image to pdf
        try:
            #clear tkinter signature canvas
            self.tkinter_signature_canvas.delete("all")

            templete_bytes = BytesIO()
            templete_bytes.write(self.pdf_to_sign)

            templete_bytes.seek(0)

            # open templete,write biometric data and save to new virual file
            trailer = PdfReader(templete_bytes)
            #
            #
            #
            trailer.Info.biometric_date=str(self.biometric_data)
            PdfWriter(templete_bytes, trailer=trailer).write()

            # signature_canvas.drawPath()
            self.signature_canvas.save()


            #set position to 0
            self.singature_bytes.seek(0)
            templete_bytes.seek(0)



            #merge signature and templete dpf bytes
            signature = PageMerge().add(PdfReader(self.singature_bytes).pages[0])[0]
            # trailer = PdfReader(templete_bytes)

            #add signature to all pages
            for page in trailer.pages:
                PageMerge(page).add(signature).render()

            #save merged result to new res.pdf file


            res_bytes=BytesIO()
            # PdfWriter('res.pdf', trailer=trailer).write()
            PdfWriter(res_bytes, trailer=trailer).write()
            res_bytes.seek(0)
            self.bytes=res_bytes.getvalue()
            res_bytes.close()


        except Exception as e:
            print(e)
        finally:

            #clear global variables and define again
            self.singature_bytes.close()
            templete_bytes.close()
            self.reinit_global_var()


            self.localstatus=False


    def windowloop(self):


        while self.localstatus:

            self.master.update_idletasks()
            self.master.update()

        else:
            self.master.withdraw()


