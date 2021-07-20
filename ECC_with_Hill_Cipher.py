from PIL import Image,ImageTk
import copy
from flask import Flask, request, jsonify, render_template, redirect, url_for, abort,send_from_directory
import imghdr
import os 
from werkzeug.utils import secure_filename



def pointAdd(Q, G, p):
    s = (((G[1]-Q[1])%p)*mmi(G[0]-Q[0], p))%p
    xNew = (pow(s, 2, p) - ((G[0]+Q[0])%p))%p
    yNew = (((s*((Q[0]-xNew)%p))%p) - (Q[1]%p))%p
    return [xNew, yNew]

def pointDouble(G, p, a):
    s = (((3*pow(G[0], 2, p) + (a%p))%p)*mmi(2*G[1], p))%p
    xNew = (pow(s, 2, p) - ((2*G[0])%p))%p
    yNew = yNew = (((s*((G[0]-xNew)%p))%p) - (G[1]%p))%p
    return [xNew, yNew]

def kTimesG(k, G, p, a):
    Q = [0, 0]
    for i in range(len(k)):
        if k[i]=="1":
            Q = pointAdd(Q, G, p)
        G = pointDouble(G, p, a)
    return [Q[0], Q[1]]

def power(x, y, m):
    if (y == 0) :
        return 1
    p = power(x, y // 2, m) % m
    p = (p * p) % m
    if(y % 2 == 0) :
        return p 
    else : 
        return ((x * p) % m)

def mmi(a0, p):
    return power(a0, p-2, p)

def MUL(A, B):
    x = A[0]*B[0][0] + A[1]*B[1][0] + A[2]*B[2][0] + A[3]*B[3][0]
    y = A[0]*B[0][1] + A[1]*B[1][1] + A[2]*B[2][1] + A[3]*B[3][1]
    z = A[0]*B[0][2] + A[1]*B[1][2] + A[2]*B[2][2] + A[3]*B[3][2]
    w = A[0]*B[0][3] + A[1]*B[1][3] + A[2]*B[2][3] + A[3]*B[3][3]
    return [x%256, y%256, z%256, w%256]

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024        #16MB limit
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['UPLOAD_PATH'] = 'static/uploads'
app.config['ENCRYPTION_PATH']='static/images/encryptedimages'
app.config['DECRYPTION_PATH']='static/images/decryptedimages'

@app.route('/')
def home():
    return render_template('homepage.html')
    


    
    
@app.route('/encryption',methods=['POST'])
def encryptpage():
    return render_template('encryption.html')

@app.route('/encryption/input',methods=['POST'])
def encryption():  
    #Let us define the ECC Parameters now. 
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            abort(400)
            return 'Please upload an image to perform Encryption'
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'],filename))       
    testImg = os.path.join(app.config['UPLOAD_PATH'],filename)
    img = Image.open(testImg)
    img = img.convert("RGB")
    
    #Let us define the ECC Parameters now. 
    
    p = 8948962207650232551656602815159153422162609644098354511344597187200057010413552439917934304191956942765446530386427345937963894309923928536070534607816947
    a = 6294860557973063227666421306476379324074715770622746227136910445450301914281276098027990968407983962691151853678563877834221834027439718238065725844264138
    b = 3245789008328967059274849584342077916531909009637501918328323668736179176583263496463525128488282611559800773506973771797764811498834995234341530862286627
    x0 = 6792059140424575174435640431269195087843153390102521881468023012732047482579853077545647446272866794936371522410774532686582484617946013928874296844351522
    y0 = 6592244555240112873324748381429610341312712940326266331327445066687010545415256461097707483288650216992613090185042957716318301180159234788504307628509330
    
    G = [x0, y0]
    xCurr = G[0]
    yCurr = G[1]
    
    alpha = bin(9426890448883247745626185743057242473809693764078951663494238777294707070023223798882976159207729119823605850588608460429412647567360897409117209856022401)[2:][::-1]
    beta = bin(9619275968248211985332842594956369871234381391917297615810447731933374561248187549880587917558907265126128418967967816764706783230897486752408974005133)[2:][::-1]
    #print(alpha, beta)
    
    alphaG = kTimesG(alpha, G, p, a)
    betaG = kTimesG(beta, G, p, a)
    
    #(alpha*beta)%p                        
    alphaBetaG = kTimesG(alpha, betaG, p, a)
    
    x = alphaBetaG[0]
    y = alphaBetaG[1]
    x = bin(x)[2:][::-1]
    y = bin(y)[2:][::-1]
    
    xG = kTimesG(x, G, p, a)
    yG = kTimesG(y, G, p, a)
    
    k = [xG, yG]
    
    K11 = copy.deepcopy(k)
    K12 = [[1-K11[0][0], 0-K11[0][1]], [0-K11[1][0], 1-K11[1][1]]]
    K21 = [[1+K11[0][0], K11[0][1]], [K11[1][0], 1+K11[1][1]]]
    K22 = [[-1*k[0][0], -1*k[0][1]], [-1*k[1][0], -1*k[1][1]]]
    
    Km = [[K11[0][0], K11[0][1], K12[0][0], K12[0][1]],
          [K11[1][0], K11[1][1], K12[1][0], K12[1][1]],
          [K21[0][0], K21[0][1], K22[0][0], K22[0][1]],
          [K21[1][0], K21[1][1], K22[1][0], K22[1][1]]]
    
    #print(Km)
    
    w, h = img.size
    #print(w,h)
    encryptedImg = Image.new(img.mode, img.size)
    eI = encryptedImg.load()
    matR = []
    matG = []
    matB = []
    for i in range(0, h, 4):
        for j in range(0, w, 4):
            matR = []
            matG = []
            matB = []
            for a0 in range(4):
                rowR = []
                rowG = []
                rowB = []
                for b0 in range(4):
                    R, G, B = img.getpixel((i+a0, j+b0))
                    rowR.append(int(R))
                    rowG.append(int(G))
                    rowB.append(int(B))
                matR.append(rowR)
                matG.append(rowG)
                matB.append(rowB)
            for a0 in range(4):
                R = MUL(Km[a0], matR)
                G = MUL(Km[a0], matG)
                B = MUL(Km[a0], matB)
                for b0 in range(4):
                    eI[i+a0, j+b0] = (R[b0], G[b0], B[b0])
        
    encryptedImg.save(os.path.join(app.config['ENCRYPTION_PATH'],filename))
    return send_from_directory(app.config['ENCRYPTION_PATH'],filename)

"""@app.route('/encryption/success')
def encryption_result(filename):
    return render_template('result.html',file=filename)

@app.route('/encryption/success')
def Encryption_result(filename):
    return 
"""
@app.route('/decryption',methods=['POST'])
def decryptpage():
    return render_template('decryption.html')

@app.route('/decryption/',methods=['POST'])
def decryption():
    
    
    #Let us define the ECC Parameters now. 

    p = 8948962207650232551656602815159153422162609644098354511344597187200057010413552439917934304191956942765446530386427345937963894309923928536070534607816947
    a = 6294860557973063227666421306476379324074715770622746227136910445450301914281276098027990968407983962691151853678563877834221834027439718238065725844264138
    b = 3245789008328967059274849584342077916531909009637501918328323668736179176583263496463525128488282611559800773506973771797764811498834995234341530862286627
    x0 = 6792059140424575174435640431269195087843153390102521881468023012732047482579853077545647446272866794936371522410774532686582484617946013928874296844351522
    y0 = 6592244555240112873324748381429610341312712940326266331327445066687010545415256461097707483288650216992613090185042957716318301180159234788504307628509330
    
    G = [x0, y0]
    xCurr = G[0]
    yCurr = G[1]
    
    alpha = bin(9426890448883247745626185743057242473809693764078951663494238777294707070023223798882976159207729119823605850588608460429412647567360897409117209856022401)[2:][::-1]
    beta = bin(9619275968248211985332842594956369871234381391917297615810447731933374561248187549880587917558907265126128418967967816764706783230897486752408974005133)[2:][::-1]
    #print(alpha, beta)
    
    alphaG = kTimesG(alpha, G, p, a)
    betaG = kTimesG(beta, G, p, a)
    
    #(alpha*beta)%p                        
    alphaBetaG = kTimesG(alpha, betaG, p, a)
    
    x = alphaBetaG[0]
    y = alphaBetaG[1]
    x = bin(x)[2:][::-1]
    y = bin(y)[2:][::-1]
    
    xG = kTimesG(x, G, p, a)
    yG = kTimesG(y, G, p, a)
    
    k = [xG, yG]
    
    K11 = copy.deepcopy(k)
    K12 = [[1-K11[0][0], 0-K11[0][1]], [0-K11[1][0], 1-K11[1][1]]]
    K21 = [[1+K11[0][0], K11[0][1]], [K11[1][0], 1+K11[1][1]]]
    K22 = [[-1*k[0][0], -1*k[0][1]], [-1*k[1][0], -1*k[1][1]]]
    
    Km = [[K11[0][0], K11[0][1], K12[0][0], K12[0][1]],
          [K11[1][0], K11[1][1], K12[1][0], K12[1][1]],
          [K21[0][0], K21[0][1], K22[0][0], K22[0][1]],
          [K21[1][0], K21[1][1], K22[1][0], K22[1][1]]]
    
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            abort(400)
            return 'Please upload an image to perform Encryption'
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'],filename))       
    testImg = os.path.join(app.config['ENCRYPTION_PATH'],filename) 
    img = Image.open(testImg)
    decryptedImg = Image.new(img.mode, img.size)
    dI = decryptedImg.load()
    matR = []
    matG = []
    matB = []
    w, h = img.size
    for i in range(0, h, 4):
        for j in range(0, w, 4):
            matR = []
            matG = []
            matB = []
            for a0 in range(4):
                rowR = []
                rowG = []
                rowB = []
                for b0 in range(4):
                    R, G, B = img.getpixel((i+a0, j+b0))
                    rowR.append(int(R))
                    rowG.append(int(G))
                    rowB.append(int(B))
                matR.append(rowR)
                matG.append(rowG)
                matB.append(rowB)
            for a0 in range(4):
                R = MUL(Km[a0], matR)
                G = MUL(Km[a0], matG)
                B = MUL(Km[a0], matB)
                for b0 in range(4):
                    dI[i+a0,j+b0] = (R[b0], G[b0], B[b0])
            
    decryptedImg.save(os.path.join(app.config['DECRYPTION_PATH'],filename))
    return send_from_directory(app.config['DECRYPTION_PATH'],filename)

if __name__ == "__main__":
    app.run()

