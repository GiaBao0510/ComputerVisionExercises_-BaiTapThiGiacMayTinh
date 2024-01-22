#------------------------------Detect object----------------------------------------------

from IPython.display import display, Javascript, Image  #Thư viện này cung cấp các hàm để hiển thị các yếu tố trong notebook Colab, bao gồm văn bản, hình ảnh, video, đồ thị, v.v.
from google.colab.output import eval_js                 #Thư viện này cung cấp các tiện ích cụ thể cho Colab, như hàm eval_js để chạy mã JavaScript trong notebook.
from base64 import b64decode, b64encode                 #Thư viện này cung cấp các hàm mã hóa và giải mã base64, thường được dùng để truyền dữ liệu binary như hình ảnh trong các môi trường như web
import cv2                                              #Thư viện OpenCV nổi tiếng về xử lý ảnh và computer vision
import numpy as np                                      #Thư viện NumPy xử lý các mảng đa chiều hiệu quả, thường được dùng trong xử lý ảnh và khoa học máy.
import PIL                                              # Thư viện Pillow, một gói mở rộng của PIL, dùng để xử lý ảnh định dạng PIL.
import io                                               #Thư viện io cung cấp các công cụ xử lý các luồng dữ liệu, hữu ích khi làm việc với hình ảnh.
import html                                             # Thư viện này cung cấp các công cụ xử lý mã HTML, có thể liên quan đến cách hiển thị ảnh trong notebook.
import time                                             # Thư viện time cung cấp các hàm liên quan đến thời gian, có thể được dùng để tính toán thời gian xử lý ảnh.

def video_stream():
  js = Javascript('''
    var video;
    var div = null;
    var stream;
    var captureCanvas;
    var imgElement;
    var labelElement;
    
    var pendingResolve = null;
    var shutdown = false;
    
    //Hàm này dọn dẹp các thành phần liên quan đến webcam:
    function removeDom() {
       stream.getVideoTracks()[0].stop();   //Ngắt kết nối video track của stream.
       
       //Xóa element video và div khỏi DOM.
       video.remove();
       div.remove();

       //Thiết lập giá trị null cho các biến liên quan
       video = null;
       div = null;
       stream = null;
       imgElement = null;
       captureCanvas = null;
       labelElement = null;
    }
    
    //Hàm này được gọi liên tục theo từng frame của animation:
    function onAnimationFrame() {
      //Kiểm tra shutdown xem có dừng webcam hay không. Nếu chưa dừng thì tiếp tục gọi lại hàm này trong frame tiếp theo.
      if (!shutdown) {
        window.requestAnimationFrame(onAnimationFrame);
      }
      //Kiểm tra pendingResolve xem có promise đang chờ capture ảnh hay không.
      if (pendingResolve) { //Nếu có promise chờ thì
        var result = "";

        //Nếu có promise chờ thì
        if (!shutdown) {
          //Lấy context 2D của canvas - Dùng hàm drawImage để vẽ frame hiện tại của video lên canvas.
          captureCanvas.getContext('2d').drawImage(video, 0, 0, 640, 480);
          
          //Lấy dữ liệu ảnh từ canvas dưới dạng base64 string.
          result = captureCanvas.toDataURL('image/jpeg', 0.8)
        }
        var lp = pendingResolve;    //Lưu resolve của promise vào một biến tạm lp.
        pendingResolve = null;      //Thiết lập pendingResolve về null.
        lp(result);                 //Gọi hàm resolve của promise (đã lưu vào lp) với dữ liệu ảnh.
      }
    }
    
    async function createDom() {
      if (div !== null) {
        return stream;
      }

      div = document.createElement('div');    //Tạo ra 1 phần tử <div></div>
      
      //Bố trí diện mạo cho phần tử này
      div.style.border = '2px solid black';
      div.style.padding = '3px';
      div.style.width = '100%';
      div.style.maxWidth = '600px';
      document.body.appendChild(div);
      
      //Tạo thẻ <div></div> gán vào modelOut
      const modelOut = document.createElement('div');
      modelOut.innerHTML = "<span>Status:</span>";    //Dòng lệnh này sử dụng thuộc tính innerHTML của thẻ <div> để thêm nội dung vào thẻ. Nội dung được thêm vào là một thẻ <span> với nội dung là "Status:", được đặt ở giữa cặp thẻ.

      labelElement = document.createElement('span');
      labelElement.innerText = 'No data';             //Thêm nội dung vào giữa cặp thẻ
      labelElement.style.fontWeight = 'bold';         //Thêm thuộc tính độ dậm cho chữ
      modelOut.appendChild(labelElement);             //Thêm nội dung đối tượng labelElement vào trong đối tượng modelOut
      div.appendChild(modelOut);                      //Thêm nội dung đối tượng modelOut vào trong đối tượng div
           
      //Tạo thẻ <video></video> gán vào video     
      video = document.createElement('video');
      video.style.display = 'block';                      //Thêm thuộc tính display:block cho thẻ video
      video.width = div.clientWidth - 6;                  //Đặt chiều rộng của thẻ video bằng chiều rộng của phần tử div trừ đi 6px.
      video.setAttribute('playsinline', '');              //Đặt thuộc tính playsinline của thẻ video thành '' để cho phép video phát trong iframe.
      video.onclick = () => { shutdown = true; };         //Nếu bấm vào đối tượng này sẽ gán shutdown là true
      stream = await navigator.mediaDevices.getUserMedia(   //Dòng code này sử dụng phương thức getUserMedia() của đối tượng navigator.mediaDevices 
          {video: { facingMode: "environment"}}             //> để lấy luồng video từ webcam. Phương thức này trả về một lời hứa. Khi lời hứa được hoàn thành, 
      );                                                    //> nó sẽ trả về một đối tượng MediaStream chứa luồng video.
      div.appendChild(video);                             //Thêm nội dung đối tượng video vào trong đối tượng div

      //Tạo thẻ <img></img> gán vào imgElement
      imgElement = document.createElement('img');
      imgElement.style.position = 'absolute';           //Đặt thuộc tính position của thẻ img có giá trị là absolute 
      imgElement.style.zIndex = 1;                      //Đặt thuộc tính zIndex của thẻ img có giá trị là 1 
      imgElement.onclick = () => { shutdown = true; };  //Nếu bấm vào đối tượng này sẽ gán shutdown là true
      div.appendChild(imgElement);                      //Thêm nội dung đối tượng img vào trong đối tượng div
      
      //Tạo thẻ <div></div> gán vào instruction
      const instruction = document.createElement('div');

      //Thêm phần tử span đã được lên thuộc tính
      instruction.innerHTML = 
          '<span style="color: red; font-weight: bold;">' +
          'When finished, click here or on the video to stop this demo</span>';
      div.appendChild(instruction);                       //Thêm nội dung đối tượng instruction vào trong đối tượng div
      instruction.onclick = () => { shutdown = true; };   //Nếu bấm vào đối tượng này sẽ gán shutdown là true
      
      video.srcObject = stream;
      await video.play();

      captureCanvas = document.createElement('canvas');
      captureCanvas.width = 640; //video.videoWidth;
      captureCanvas.height = 480; //video.videoHeight;

      /*Dòng code này yêu cầu trình duyệt gọi lại hàm onAnimationFrame trong frame tiếp theo. 
        Hàm onAnimationFrame sẽ được gọi liên tục để cập nhật video và xử lý capture ảnh khi cần. */
      window.requestAnimationFrame(onAnimationFrame);
      
      return stream;
    }
    async function stream_frame(label, imgData) {
      //shutdown là true thì sẽ thực hiện tắt
      if (shutdown) {
        removeDom();
        shutdown = false;
        return '';
      }

      var preCreate = Date.now();   //Lấy thời gian trước khi tạo luồng
      stream = await createDom();
      
      var preShow = Date.now();     //Lấy thời gian trước khi hiển thị
      if (label != "") {
        labelElement.innerHTML = label;
      }
            
      if (imgData != "") {
        var videoRect = video.getClientRects()[0];
        imgElement.style.top = videoRect.top + "px";
        imgElement.style.left = videoRect.left + "px";
        imgElement.style.width = videoRect.width + "px";
        imgElement.style.height = videoRect.height + "px";
        imgElement.src = imgData;
      }
      
      var preCapture = Date.now();        // Lấy thời gian trước khi chụp ảnh.

      /*
            Tạo một promise và đợi kết quả:
            - Bên trong promise, gán resolve (hàm resolve của promise) vào biến pendingResolve.
            - Khi hàm onAnimationFrame nhận được yêu cầu chụp ảnh, nó sẽ gọi hàm pendingResolve với dữ liệu ảnh captured.
       */
      var result = await new Promise(function(resolve, reject) {
        pendingResolve = resolve;
      });
      shutdown = false;                 //Thiết lập shutdown về false
      
      //Trả về một object chứa thông tin thời gian xử lý:
      return {'create': preShow - preCreate,      //Thời gian tạo luồng video.
              'show': preCapture - preShow,       // Thời gian hiển thị video và overlay.
              'capture': Date.now() - preCapture, // Thời gian chụp ảnh.
              'img': result};                     //Dữ liệu ảnh chụp được.
    }
    ''')

  display(js)
  
#2. lấy hai đối số là nhãn và tọa độ khung hình của webcam. Hàm này sẽ chạy mã JavaScript sau
def video_frame(label, bbox):
  data = eval_js('stream_frame("{}", "{}")'.format(label, bbox))
  return data

#3. Hàm này lấy một chuỗi là đối số. Chuỗi này chứa dữ liệu của một khung hình webcam được mã hóa base64
def js_to_image(js_reply):
  """
  Các thông số:
      - js_reply: đối tượng JS chứa hình ảnh từ webcam
    Trả về:
      - imge: hình ảnh Open BGR
  """
  # Giải mã hình ảnh base64e
  image_bytes = b64decode(js_reply.split(',')[1])
  # Chuyển đổi bytes thành mảng nhiều chiều
  jpg_as_np = np.frombuffer(image_bytes, dtype=np.uint8)
  # Giải mã mảng nhiều chiều thành hình ảnh OpenSV BGR
  img = cv2.imdecode(jpg_as_np, flags=1)

  return img

# Chức năng chuyển đổi hình ảnh hộp giới hạn hình chữ nhật OpenCV thành chuỗi byte base64 để được phủ trên luồng video
def bbox_to_bytes(bbox_array):
  """
  Tham số:
      - bbox_array: Mảng Numpy(pixels) chứa hình hộp chữ nhật để phủ lên luồng video
    Trả:
      - bytes: Chuỗi byte hình ảnh Base64
  """
  # Chuyển đổi mảng thành hình ảnh PIL
  bbox_PIL = PIL.Image.fromarray(bbox_array, 'RGBA')
  iobuf = io.BytesIO()
  # Định dạng bbox thành png cho việc trả về
  bbox_PIL.save(iobuf, format='png')
  # Chuỗi trả về 1 định dạng
  bbox_bytes = 'data:image/png;base64,{}'.format((str(b64encode(iobuf.getvalue()), 'utf-8')))

  return bbox_bytes

# Khỏi tạo mô hình nhận diện khuôn mặt Haar Cascade
face_cascade = cv2.CascadeClassifier(cv2.samples.findFile(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'))

# Bắt đầu truyền phát video từ webcamm
video_stream()
# Nhãn cho video
label_html = 'Capturing...'
# Khởi tạo hộp giới hạn để trống
bbox = ''
count = 0 
while True:
    js_reply = video_frame(label_html, bbox)
    if not js_reply:
        break

    # Chuyển đổi phản hồi JS thành hình ảnh OpenCV
    img = js_to_image(js_reply["img"])

    # Tạo lớp phủ trong suôt trong hình hộp giới hạn
    bbox_array = np.zeros([480,640,4], dtype=np.uint8)

    # Hình ảnh thanh đo độ sang để nhận diện khuôn mặt
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # Lấy tọa độ vùng mặt
    faces = face_cascade.detectMultiScale(gray)
    # Lấy hộp giới hạn khuôn mặt cho lớp phủ
    for (x,y,w,h) in faces:
      bbox_array = cv2.rectangle(bbox_array,(x,y),(x+w,y+h),(255,0,0),2)

    bbox_array[:,:,3] = (bbox_array.max(axis = 2) > 0 ).astype(int) * 255
    # Chuyển đổi lớp phủ của bbox thành byte
    bbox_bytes = bbox_to_bytes(bbox_array)
    # Cập nhập bbox để khung tiếp theo có lớp phủ bbox
    bbox = bbox_bytes