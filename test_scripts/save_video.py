import pyrealsense2 as rs
import numpy as np
import cv2
from datetime import datetime
  
# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()

# Get device product line for setting a supporting resolution
pipeline_wrapper = rs.pipeline_wrapper(pipeline)
pipeline_profile = config.resolve(pipeline_wrapper)
device = pipeline_profile.get_device()
device_product_line = str(device.get_info(rs.camera_info.product_line))

found_rgb = False
for s in device.sensors:
    if s.get_info(rs.camera_info.name) == 'RGB Camera':
        found_rgb = True
        break
if not found_rgb:
    print("The demo requires Depth camera with Color sensor")
    exit(0)

config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# name by datetime
current = datetime.now()
dt_string = current.strftime("%Y-%m-%d.%H.%M.%S")

video_out = cv2.VideoWriter(dt_string+"_video.avi", cv2.VideoWriter_fourcc(*'XVID'), 30, (640, 480))
depth_out = cv2.VideoWriter(dt_string+"_depth.avi", cv2.VideoWriter_fourcc(*'XVID'), 30, (640, 480))
zero_pad = np.zeros((640, 480))
# Start streaming
pipeline.start(config)
align_to = rs.stream.color
align = rs.align(align_to)
try:
    while True:
        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        aligned_frames = align.process(frames)
        depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()
        if not depth_frame or not color_frame:
            continue

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        color_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
        depth_image = np.array(np.bitwise_and(depth_image, 0xFF), np.bitwise_and(depth_image, 0xFF00), zero_pad)
        
        video_out.write(color_image)
        depth_out.write(depth_image)        

finally:
    # Stop streaming
    pipeline.stop()