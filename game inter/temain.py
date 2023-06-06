import cv2 as cv
import numpy as np
import mediapipe as mp
import random

LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]

LEFT_IRIS = [474, 475, 476, 477]
RIGHT_IRIS = [469, 470, 471, 472]

FACE_HEAD_POSE_LANDMARKS = [1, 33, 61, 199, 291, 263]

face_2d = []
face_3d = []

compensated_angle = [0, 0, 0]

coords_dict = {(5, 5): 'coord_1', (350, 5): 'coord_2', (175, 5): 'coord_3',
               (175, 540): 'coord_4', (350, 540): 'coord_5', (5, 540): 'coord_6',
               (350, 270): 'coord_7', (5, 270): 'coord_8'}

# 랜덤한 좌표 선택
rand_key = random.choice(list(coords_dict.keys()))
rand_coords = coords_dict[rand_key]

capture = cv.VideoCapture(0)

assert_tool = cv.imread('tool_small.png', cv.IMREAD_UNCHANGED)
abj = 0

mp_face_mesh = mp.solutions.face_mesh

with mp_face_mesh.FaceMesh(max_num_faces=1,
                           refine_landmarks=True,
                           min_detection_confidence=0.5,
                           min_tracking_confidence=0.5
                           ) as face_mesh:
    while True:
        if capture.get(cv.CAP_PROP_POS_FRAMES) == capture.get(cv.CAP_PROP_FRAME_COUNT):
            capture.set(cv.CAP_PROP_POS_FRAMES, 0)
        ret, frame = capture.read()
        frame = cv.flip(frame, 1)
        if not ret:
            print('Error')
            break
        img_h, img_w = frame.shape[:2]
        results = face_mesh.process(frame)
        if results.multi_face_landmarks:
            mesh_points = np.array([np.multiply([p.x, p.y], [img_w, img_h]).astype(int)
                                    for p in results.multi_face_landmarks[0].landmark])

            gaze_point = (int(mesh_points[0][0]), int(mesh_points[0][1]))  # 눈의 중심 좌표 사용

            for pt in mesh_points:
                cv.circle(frame, pt, 1, (255, 255, 255), -1, cv.LINE_AA)
                pass
            cv.polylines(frame, [mesh_points[LEFT_EYE]], True, (0, 0, 255), 2, cv.LINE_AA)
            cv.polylines(frame, [mesh_points[RIGHT_EYE]], True, (0, 0, 255), 2, cv.LINE_AA)
            # 눈동자
            cv.polylines(frame, [mesh_points[LEFT_IRIS]], True, (0, 255, 0), 2, cv.LINE_AA)
            cv.polylines(frame, [mesh_points[RIGHT_IRIS]], True, (0, 255, 0), 2, cv.LINE_AA)

            (l_cx, l_cy), l_rad = cv.minEnclosingCircle(mesh_points[LEFT_IRIS])
            (r_cx, r_cy), r_rad = cv.minEnclosingCircle(mesh_points[RIGHT_IRIS])
            l_center = np.array([l_cx, l_cy], dtype=np.int32)
            r_center = np.array([r_cx, r_cy], dtype=np.int32)
            cv.circle(frame, l_center, int(l_rad), (0, 255, 0), 2, cv.LINE_AA)
            cv.circle(frame, r_center, int(r_rad), (0, 255, 0), 2, cv.LINE_AA)

            for pt in mesh_points:
                (cx, cy) = pt[0], pt[1]
                cv.circle(frame, [cx, cy], 1, (255, 255, 255), -1, cv.LINE_AA)

            for idx, lm in enumerate(results.multi_face_landmarks[0].landmark):
                if idx in FACE_HEAD_POSE_LANDMARKS:
                    if idx == 1:
                        nose_2d = (lm.x * img_w, lm.y * img_h)
                        nose_3d = (lm.x * img_w, lm.y * img_h, lm.z * 3000)

                    x, y = int(lm.x * img_w), int(lm.y * img_h)

                    face_2d.append([x, y])
                    face_3d.append([x, y, lm.z])

            face_2d = np.array(face_2d, dtype=np.float64)

            face_3d = np.array(face_3d, dtype=np.float64)

            focal_len = 1 * img_w

            camera_mat = np.array([[focal_len, 0, img_h / 2],
                                   [0, focal_len, img_w / 2],
                                   [0, 0, 1]])

            dist_mat = np.zeros((4, 1), dtype=np.float64)

            success, rot_vec, trans_vec = cv.solvePnP(face_3d, face_2d, camera_mat, dist_mat)

            rot_mat, jac = cv.Rodrigues(rot_vec)
            angles, mtxR, mtxQ, Qx, Qy, Qz = cv.RQDecomp3x3(rot_mat)
            x = angles[0] * 360
            y = angles[1] * 360
            z = angles[2] * 360

            # nose_3d_projection, jacobian = cv.projectPoints(nose_3d, rot_vec, trans_vec, camera_mat, dist_mat)

            p1 = (int(nose_2d[0]), int(nose_2d[1]))
            p2 = (int(nose_2d[0] + y * 10), int(nose_2d[1] - x * 10))

            cv.line(frame, p1, p2, (255, 255, 0), 3)

            face_2d = []
            face_3d = []

        img_tool = assert_tool.copy()

        _, mask = cv.threshold(img_tool[:, :, 3], 1, 255, cv.THRESH_BINARY)
        mask_inverse = cv.bitwise_not(mask)

        # 좌표 추출
        x, y = rand_key

        img_tool = cv.cvtColor(img_tool, cv.COLOR_BGRA2BGR)
        height, width = img_tool.shape[:2]

        # 이미지를 합치는 부분 수정
        roi = frame[x:x + height, y:y + width]
        masked_roi = cv.bitwise_and(roi, roi, mask=mask_inverse)
        masked_tool = cv.bitwise_and(img_tool, img_tool, mask=mask)
        combined_roi = cv.add(masked_roi, masked_tool)
        frame[x:x + height, y:y + width] = combined_roi

        marker_list = []
        gaze_list = []
        # 시선 위치와 이미지 위치가 일치하면, 새로운 랜덤 좌표 할당
        if abs(p2[0] - rand_key[1]) < 40 and abs(p2[1] - rand_key[0]) < 40:
            print(rand_key[1], rand_key[0])
            print('(', p2[0], p2[1], ')')
            marker_list.append(rand_key[1])
            marker_list.append(rand_key[0])
            gaze_list.append(p2[0])
            marker_list.append(p2[1])

            rand_key = random.choice(list(coords_dict.keys()))
            rand_coords = coords_dict[rand_key]


        # print("main : ", p2)
        # print("rand_x :", rand_key[1], " / rand_y :", rand_key[0])

        def calibrate_gaze(marker_list, gaze_list, camera_matrix, dist_coeffs):
            # Convert marker and gaze points to numpy arrays
            marker_points = np.array(marker_list, dtype=np.float32)
            gaze_points = np.array(gaze_list, dtype=np.float32)

            # Estimate the pose of the camera relative to the marker
            _, rvec, tvec = cv.solvePnP(marker_points, gaze_points, camera_matrix, dist_coeffs)

            # Convert rotation vector to rotation matrix
            rot_mat, _ = cv.Rodrigues(rvec)

            # Invert rotation matrix and translation vector to get camera pose relative to gaze
            inv_rot_mat = rot_mat.transpose()
            inv_tvec = -inv_rot_mat.dot(tvec)

            # Calculate gaze direction vector
            gaze_dir = inv_rot_mat.dot(np.array([0, 0, 1]))

            # Calculate calibration factor
            calib_factor = inv_tvec[2] / gaze_dir[2]

            # Calculate calibrated gaze points
            calibrated_gaze = []
            for gaze_point in gaze_points:
                # Calculate 3D position of gaze point
                gaze_pos_3d = inv_rot_mat.dot(np.array([gaze_point[0], gaze_point[1], 1])) * calib_factor + inv_tvec
                # Calculate 2D position of gaze point using camera matrix
                gaze_pos_2d, _ = cv.projectPoints(gaze_pos_3d, rvec, tvec, camera_matrix, dist_coeffs)
                calibrated_gaze.append(gaze_pos_2d.squeeze().tolist())

            return calibrated_gaze


        cv.imshow('main', frame)

        key = cv.waitKey(1)
        if key == ord('q'):
            break

capture.release()
cv.destroyAllWindows()