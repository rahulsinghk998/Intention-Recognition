import vtk
import time
import numpy as np

#-------------------------------------------#
#     Qt viewer for UI for angle change     #
#-------------------------------------------#

#PPT on Transformation: http://vtk.org/Wiki/VTK/Presentations
#vtkActor.SetPosition() simply effects where your actor is rendered, but do not modify any coordinates of the underlying polydata physically.  
#SetCenter() apply a vtkTransformFilter to modify point coordinates actually.
#Cube box outline for an actor: https://www.vtk.org/Wiki/VTK/Examples/Cxx/PolyData/Outline
#VTK Bitbucket Examples: https://gitlab.kitware.com/vtk/vtk/tree/master/Examples

# Add the observers to watch for particular events. These invoke Python functions.
Rotating= 0
Panning = 0
Zooming = 0

rotFlagRU = 0 #Flag for rotating right upper arm with interaction with mouse or keyboard
rotFlagRF = 0 #Flag for rotating right fore arm with interaction with mouse or keyboard

# Handle the mouse button events.
def ButtonEvent(obj, event):
    global Rotating, Panning, Zooming, rotFlagRU, rotFlagRF
    if ((event == "LeftButtonPressEvent")):
        Rotating = 1
        #torso.RotateX(30)
        #axes.RotateX(30)
        if (rotFlagRU==1):
            upperArmR.RotateX(30)
        if (rotFlagRF==1):
            upperArmL.RotateX(30)
        renWin.Render()
    elif ((event == "LeftButtonReleaseEvent")):
        Rotating = 0
    elif ((event == "MiddleButtonPressEvent")):
        Panning = 1
        if (rotFlagRU==1):
            upperArmR.RotateZ(30)
        if (rotFlagRF==1):
            upperArmL.RotateZ(30)
        renWin.Render()
    elif ((event == "MiddleButtonReleaseEvent")):
        Panning = 0
    elif ((event == "RightButtonPressEvent")):
        Zooming = 1
        if (rotFlagRU==1):
            upperArmR.RotateY(30)
        if (rotFlagRF==1):
            upperArmL.RotateY(30)
        renWin.Render()
    elif ((event == "RightButtonReleaseEvent")):
        Zooming = 0

# General high-level logic
def MouseMove(obj, event):
    global Rotating, Panning, Zooming
    global iren, renWin, ren
    lastXYpos = iren.GetLastEventPosition()
    lastX = lastXYpos[0]
    lastY = lastXYpos[1]

    xypos = iren.GetEventPosition()
    x = xypos[0]
    y = xypos[1]

    center = renWin.GetSize()
    centerX = center[0]/2.0
    centerY = center[1]/2.0

    if Rotating:
        Rotate(ren, ren.GetActiveCamera(), x, y, lastX, lastY,
               centerX, centerY)
    elif Panning:
        Pan(ren, ren.GetActiveCamera(), x, y, lastX, lastY, centerX,
            centerY)
    elif Zooming:
        Dolly(ren, ren.GetActiveCamera(), x, y, lastX, lastY,
              centerX, centerY)

def Keypress(obj, event):
    global rotFlagRU, rotFlagRF
    key = obj.GetKeySym()
    if key == "e":
        obj.InvokeEvent("DeleteAllObjects")
        sys.exit()
    elif key == "w":
        Wireframe()
    elif key =="s":
        Surface()
    elif key =="u":
        rotFlagRU = 1
        rotFlagRF = 0
    elif key == "f":
        rotFlagRF = 1
        rotFlagRU = 0
    elif key =="n":
        rotFlagRU=0
        rotFlagRF=0

# Routines that translate the events into camera motions.

# This one is associated with the left mouse button. It translates x
# and y relative motions into camera azimuth and elevation commands.
def Rotate(renderer, camera, x, y, lastX, lastY, centerX, centerY):
    camera.Azimuth(lastX-x)
    camera.Elevation(lastY-y)
    camera.OrthogonalizeViewUp()
    renWin.Render()


# Pan translates x-y motion into translation of the focal point and position.
def Pan(renderer, camera, x, y, lastX, lastY, centerX, centerY):
    FPoint = camera.GetFocalPoint()
    FPoint0 = FPoint[0]
    FPoint1 = FPoint[1]
    FPoint2 = FPoint[2]

    PPoint = camera.GetPosition()
    PPoint0 = PPoint[0]
    PPoint1 = PPoint[1]
    PPoint2 = PPoint[2]

    renderer.SetWorldPoint(FPoint0, FPoint1, FPoint2, 1.0)
    renderer.WorldToDisplay()
    DPoint = renderer.GetDisplayPoint()
    focalDepth = DPoint[2]

    APoint0 = centerX+(x-lastX)
    APoint1 = centerY+(y-lastY)

    renderer.SetDisplayPoint(APoint0, APoint1, focalDepth)
    renderer.DisplayToWorld()
    RPoint = renderer.GetWorldPoint()
    RPoint0 = RPoint[0]
    RPoint1 = RPoint[1]
    RPoint2 = RPoint[2]
    RPoint3 = RPoint[3]

    if RPoint3 != 0.0:
        RPoint0 = RPoint0/RPoint3
        RPoint1 = RPoint1/RPoint3
        RPoint2 = RPoint2/RPoint3

    camera.SetFocalPoint((FPoint0-RPoint0)/2.0 + FPoint0,
                          (FPoint1-RPoint1)/2.0 + FPoint1,
                          (FPoint2-RPoint2)/2.0 + FPoint2)
    camera.SetPosition((FPoint0-RPoint0)/2.0 + PPoint0,
                        (FPoint1-RPoint1)/2.0 + PPoint1,
                        (FPoint2-RPoint2)/2.0 + PPoint2)
    renWin.Render()

# Dolly converts y-motion into a camera dolly commands.
def Dolly(renderer, camera, x, y, lastX, lastY, centerX, centerY):
    dollyFactor = pow(1.02,(0.5*(y-lastY)))
    if camera.GetParallelProjection():
        parallelScale = camera.GetParallelScale()*dollyFactor
        camera.SetParallelScale(parallelScale)
    else:
        camera.Dolly(dollyFactor)
        renderer.ResetCameraClippingRange()

    renWin.Render()

# Wireframe sets the representation of all actors to wireframe.
def Wireframe():
    actors = ren.GetActors()
    actors.InitTraversal()
    actor = actors.GetNextItem()
    while actor:
        actor.GetProperty().SetRepresentationToWireframe()
        actor = actors.GetNextItem()

    renWin.Render()

# Surface sets the representation of all actors to surface.
def Surface():
    actors = ren.GetActors()
    actors.InitTraversal()
    actor = actors.GetNextItem()
    while actor:
        actor.GetProperty().SetRepresentationToSurface()
        actor = actors.GetNextItem()
    renWin.Render()

def makeSphere(center, radius, res):
    source = vtk.vtkSphereSource()
    source.SetCenter(center)
    source.SetRadius(radius)
    #source.SetResolution(res)
    # mapper
    mapper = vtk.vtkPolyDataMapper()
    if vtk.VTK_MAJOR_VERSION <= 5:
        mapper.SetInput(source.GetOutput())
    else:
        mapper.SetInputConnection(source.GetOutputPort())
    # actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    return actor

def makeCyl(ren, rad, height, res, centre):
    # create source
    source = vtk.vtkCylinderSource()
    source.SetCenter(centre)
    source.SetRadius(rad)
    source.SetHeight(height)
    source.SetResolution(res)
    # mapper
    mapper   = vtk.vtkPolyDataMapper()
    cylinder = source.GetOutputPort()
    mapper.SetInputConnection(cylinder)
    
    ###Outline can be added as an option to the argument###
    #outline = vtk.vtkOutlineFilter()
    #outline.SetInputData(source.GetOutput())
    #outlineMapper= vtk.vtkPolyDataMapper()
    #outlineMapper.SetInputConnection(outline.GetOutputPort())
    #outlineActor = vtk.vtkActor()
    #outlineActor.SetMapper(outlineMapper)
    #outlineActor.GetProperty().SetColor(0,0,0)
    #ren.AddActor(outlineActor)
    
    # actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    return actor

##Showing Axes for Center and Origin for any Actor##
def showAxes(ren, actor):
    transform  = vtk.vtkTransform()
    transform.Translate(actor.GetCenter())  #(25, 0.0, 0.0)
    axesActorCen = vtk.vtkAxesActor()
    axesActorCen.SetUserTransform(transform) 
    axesActorCen.SetTotalLength(20.0, 20.0, 20.0)
    #xAxisLabel = axesActor.GetXAxisCaptionActor2D()
    #xAxisLabel.GetCaptionTextProperty().SetFontSize(6)
    ren.AddActor(axesActorCen)

    transform = vtk.vtkTransform()
    transform.Translate(actor.GetOrigin())
    axesActor = vtk.vtkAxesActor()
    axesActor.SetUserTransform(transform) 
    axesActor.SetTotalLength(20.0, 20.0, 20.0)
    ren.AddActor(axesActor)
    
    return 0

def createLimb(rad, len, rot, translate, origin):
    return 0

def makeSkeleton(ren):
    # assign actor to the renderer
    torsoRad = 10
    torsoLen = 25
    torsoCen = np.array([0, torsoLen/2 , 0])
    torsoOrigin = np.array([0, torsoLen , 0])
    torso    = makeCyl(ren, torsoRad, torsoLen, 100, torsoCen)
    torso.SetOrigin(torsoOrigin)
    ren.AddActor(torso)
    
    uArmRad    = 4
    uArmLen    = 20
    uArmCenR    = torsoOrigin - np.array([(uArmLen/2 + torsoRad), 0, 0])
    uArmOriginR = torsoOrigin - np.array([torsoRad, 0, 0])
    upperArmR   = makeCyl(ren, uArmRad, uArmLen, 100, (0,0,0)) # uArmCen)
    upperArmR.SetOrigin((0,uArmLen/2, 0))
    transform  = vtk.vtkTransform()
    transform.PostMultiply()
    transform.RotateZ(-90)
    transform.Translate(-torsoRad - uArmLen/2, torsoLen, 0)
    upperArmR.SetUserTransform(transform)
    #upperArmR.SetOrigin((-20.0, 25.0, 0.0))
    #upperArm.SetPosition(uArmCen)
    #upperArm.SetOrientation(0,0,-90)
    ren.AddActor(upperArmR)
    
    uArmCenL    = torsoOrigin + np.array([(uArmLen/2 + torsoRad), 0, 0])
    uArmOriginL = torsoOrigin + np.array([torsoRad, 0, 0])
    upperArmL   = makeCyl(ren, uArmRad, uArmLen, 100, (0,0,0))
    upperArmL.SetOrigin((0,uArmLen/2, 0))
    transform  = vtk.vtkTransform()
    transform.PostMultiply()
    transform.RotateZ(90)
    transform.Translate(torsoRad + uArmLen/2, torsoLen, 0)
    upperArmL.SetUserTransform(transform)
    ren.AddActor(upperArmL)
    
    fArmRad    = 2.5
    fArmLen    = 20
    fArmCenR    = torsoOrigin - np.array([(fArmLen/2 + torsoRad), 0, 0])
    fArmOriginR = torsoOrigin - np.array([torsoRad, 0, 0])
    foreArmR  = makeCyl(ren, fArmRad, fArmLen, 100, (0,0,0))
    foreArmR.SetOrigin((0,fArmLen/2, 0))
    transform  = vtk.vtkTransform()
    transform.PostMultiply()
    transform.RotateZ(-90)
    transform.Translate(-torsoRad - uArmLen - fArmLen/2, torsoLen, 0)
    foreArmR.SetUserTransform(transform)
    ren.AddActor(foreArmR)
    
    fArmCenL    = torsoOrigin + np.array([(fArmLen/2 + torsoRad), 0, 0])
    fArmOriginL = torsoOrigin + np.array([torsoRad, 0, 0])
    foreArmL  = makeCyl(ren, fArmRad, fArmLen, 100, (0,0,0))
    foreArmL.SetOrigin((0,fArmLen/2, 0))
    transform  = vtk.vtkTransform()
    transform.PostMultiply()
    transform.RotateZ(90)
    transform.Translate(torsoRad + uArmLen + fArmLen/2, torsoLen, 0)
    foreArmL.SetUserTransform(transform)
    ren.AddActor(foreArmL)
    
    sphereActor = makeSphere((0, torsoLen+7, 0), 7, 100)
    ren.AddActor(sphereActor) #Add head to torso
    
    return sphereActor, torso, upperArmL, upperArmR, foreArmL, foreArmR

def setCamera(ren):
    ren.ResetCamera()                    #Reseting and setting camera angle properties
    cam1 = ren.GetActiveCamera()
    cam1.SetPosition(12.0, 3.0, 150.0)
    cam1.SetFocalPoint(12.0, 12.0, 0.0)
    ren.ResetCameraClippingRange()
    
    return 0

def addInteractor(renWin):
    # Define custom interaction.
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetInteractorStyle(None)
    iren.SetRenderWindow(renWin)

    iren.AddObserver("LeftButtonPressEvent", ButtonEvent)
    iren.AddObserver("LeftButtonReleaseEvent", ButtonEvent)
    iren.AddObserver("MiddleButtonPressEvent", ButtonEvent)
    iren.AddObserver("MiddleButtonReleaseEvent", ButtonEvent)
    iren.AddObserver("RightButtonPressEvent", ButtonEvent)
    iren.AddObserver("RightButtonReleaseEvent", ButtonEvent)
    iren.AddObserver("MouseMoveEvent", MouseMove)
    iren.AddObserver("KeyPressEvent", Keypress)
    
    return iren

def setRenWindow():
    # create a rendering window and renderer
    ren = vtk.vtkRenderer()
    ren.SetBackground(0.1, 0.2, 0.4)     #Add the actors to the renderer, set the background and size
    
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    renWin.SetSize(800, 800)
    
    return ren, renWin