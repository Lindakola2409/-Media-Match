#include <wx/wx.h>
#include <wx/timer.h>
#include <wx/dcbuffer.h>
#include <wx/time.h>
#include <filesystem>
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <math.h>
#include <unordered_set>
using namespace std;
namespace fs = std::filesystem;
const int TIMER_ID = 1000;
/**
 * Display an image using WxWidgets.
 * https://www.wxwidgets.org/
 */

/** Declarations*/
template <typename T>
struct Block
{

  Block();
  /// @brief
  void Print();
  vector<vector<T>> r;
  vector<vector<T>> g;
  vector<vector<T>> b;
};
template <typename T>
Block<T>::Block()
{
  r.assign(8, std::vector<T>(8, 0));
  g.assign(8, std::vector<T>(8, 0));
  b.assign(8, std::vector<T>(8, 0));
}

struct BlockString
{

  BlockString();
  /// @brief
  void Print();
  vector<vector<string>> r;
  vector<vector<string>> g;
  vector<vector<string>> b;
};

BlockString::BlockString()
{
  vector<string> blank;
  for (int i = 0; i < 8; i++)
  {
    blank.push_back("");
  }

  for (int i = 0; i < 8; i++)
  {
    r.push_back(blank);
    g.push_back(blank);
    b.push_back(blank);
  }
}

template <typename T>
void Block<T>::Print()
{
  cout << "Red Channel" << endl;
  for (int i = 0; i < 8; i++)
  {
    for (int j = 0; j < 8; j++)
    {
      cout << r[i][j] << " ";
    }
    cout << endl;
  }
  cout << "Blue Channel" << endl;
  for (int i = 0; i < 8; i++)
  {
    for (int j = 0; j < 8; j++)
    {
      cout << b[i][j] << " ";
    }
    cout << endl;
  }
  cout << "Green Channel" << endl;
  for (int i = 0; i < 8; i++)
  {
    for (int j = 0; j < 8; j++)
    {
      cout << g[i][j] << " ";
    }
    cout << endl;
  }
}

/**Í
 * Class that implements wxApp
 */
class MyApp : public wxApp
{
public:
  bool OnInit() override;
};

/**
 * Class that implements wxFrame.
 * This frame serves as the top level window for the program
 */
class MyFrame : public wxFrame
{
public:
  MyFrame(const wxString &title, string imagePath);
  void OnTimer(wxTimerEvent &event);
  void StartTimer(int time);
  void SetFactors(float quantizationLevel, float deliveryMode, float latency);
  void ExportToCSV();
private:
  void OnPaint(wxPaintEvent &event);
  wxImage inImage;
  wxScrolledWindow *scrolledWindow;
  int mWidth;
  int mHeight;
  int mError = 0;
  int mMaxBits = 0;
  float mQuantizationLevel = 0.0f;
  float mDeliveryMode = 0.0f;
  float mLatency = 0.0f;
  bool bIsModeComplete = false;
  int mCurrIteration = 0;
  bool bEncode = false;
  vector<int> mMode2Path;
  unsigned char *mOriginalPictureData = nullptr;
  unsigned char *mNewData = nullptr;
  
  /** Timer */
  wxDECLARE_EVENT_TABLE();
  wxTimer m_timer;
};
/** Timer */
wxBEGIN_EVENT_TABLE(MyFrame, wxFrame)
    EVT_TIMER(TIMER_ID, MyFrame::OnTimer)
        wxEND_EVENT_TABLE()

    /** Utility function to read image data */
    unsigned char *readImageData(string imagePath, int width, int height, unsigned char *&originalPictureData);

/** Definitions */

/**
 * Init method for the app.
 * Here we process the command line arguments and
 * instantiate the frame.
 */
bool MyApp::OnInit()
{
  wxInitAllImageHandlers();

  // deal with command line arguments here
  // cout << "Number of command line arguments: " << wxApp::argc << endl;
  if (wxApp::argc != 5)
  {
    cerr << "The executable should be invoked with exactly one filepath "
            "argument followed by the quantization level, mode, and latency. Example ./MyImageApplication ../test2.rgb 7 1 0"
         << endl;
    exit(1);
  }
  
  float quantizationLevel = wxAtof(wxApp::argv[2]);
  float deliveryMode = wxAtof(wxApp::argv[3]);
  float latency = wxAtof(wxApp::argv[4]);
  cout << "Quantization Level: " << quantizationLevel << endl;
  cout << "deliveryMode: " << deliveryMode << endl;
  cout << "latency: " << latency << endl;

  if (quantizationLevel < 0 || quantizationLevel > 7)
  {
    cerr << "The quantization level must be between [0,7] inclusive. Please enter valid quantization level."
         << endl;
    exit(1);
  }
  string imagePath = wxApp::argv[1].ToStdString();
  string windowTitle = "CSCI 576 | Mode: " + wxApp::argv[3].ToStdString() + " | Quantization level: " + wxApp::argv[2].ToStdString() + " | Latency: " + wxApp::argv[4].ToStdString() + " ms";
  MyFrame *frame = new MyFrame(windowTitle, imagePath);
  frame->Show(true);
  frame->SetFactors(quantizationLevel, deliveryMode, latency);
  /*Timer*/
  if (latency == 0)
  {
    latency = 1;
  }
  frame->StartTimer(latency);
  return true;
}

/**
 * Constructor for the MyFrame class.
 * Here we read the pixel data from the file and set up the scrollable window.
 */
MyFrame::MyFrame(const wxString &title, string imagePath)
    : wxFrame(NULL, wxID_ANY, title), m_timer(this, TIMER_ID)
{

  // Modify the height and width values here to read and display an image with
  // different dimensions.
  mWidth = 1024;
  mHeight = 512;

  unsigned char *inData = readImageData(imagePath, 512, 512, mOriginalPictureData);

  // the last argument is static_data, if it is false, after this call the
  // pointer to the data is owned by the wxImage object, which will be
  // responsible for deleting it. So this means that you should not delete the
  // data yourself.
  inImage.SetData(inData, 512, 512, false);
  mNewData = (unsigned char *)malloc(1024 * 512 * 3 * sizeof(unsigned char));
  mOriginalPictureData = readImageData(imagePath, 512, 512, mOriginalPictureData);

  for (int y = 0; y < mHeight; ++y)
  {
    for (int x = 0; x < 1024; ++x)
    {
      mNewData[(y * mWidth + x) * 3] = 0;
      mNewData[(y * mWidth + x) * 3 + 1] = 0;
      mNewData[(y * mWidth + x) * 3 + 2] = 0;
    }
  }

  for (int y = 0; y < mHeight; ++y)
  {
    for (int x = 0; x < 512; ++x)
    {
      int index = (y * mHeight + x) * 3;
      mNewData[(y * mWidth + x) * 3] = mOriginalPictureData[index];
      // G
      mNewData[(y * mWidth + x) * 3 + 1] = mOriginalPictureData[index + 1];
      // B
      mNewData[(y * mWidth + x) * 3 + 2] = mOriginalPictureData[index + 2];
    }
  }

  // Set up the scrolled window as a child of this frame
  scrolledWindow = new wxScrolledWindow(this, wxID_ANY);
  scrolledWindow->SetScrollbars(10, 10, mWidth, mHeight);
  scrolledWindow->SetVirtualSize(mWidth, mHeight);

  // Bind the paint event to the OnPaint function of the scrolled window
  scrolledWindow->Bind(wxEVT_PAINT, &MyFrame::OnPaint, this);

  // Set the frame size
  SetClientSize(mWidth, mHeight);

  // Set the frame background color
  SetBackgroundColour(*wxBLACK);

  /**Timer*/
  // m_timer.Start(1000);
}

void MyFrame::OnTimer(wxTimerEvent &event)
{
  scrolledWindow->Refresh();
}

/**
 * The OnPaint handler that paints the UI.
 * Here we paint the image pixels into the scrollable window.
 */
void MyFrame::OnPaint(wxPaintEvent &event)
{
  wxBufferedPaintDC dc(scrolledWindow);
  scrolledWindow->DoPrepareDC(dc);
  inImage = wxImage(mWidth, mHeight, mNewData, true);

  inImage = wxImage(mWidth, mHeight, mNewData, true);
  wxBitmap inImageBitmap = wxBitmap(inImage);
  dc.DrawBitmap(inImageBitmap, 0, 0, false);
}
/** Utility function to read image data */
unsigned char *readImageData(string imagePath, int width, int height, unsigned char *&originalPictureData)
{

  // Open the file in binary mode
  ifstream inputFile(imagePath, ios::binary);

  if (!inputFile.is_open())
  {
    cerr << "Error Opening File for Reading" << endl;
    exit(1);
  }

  // Create and populate RGB buffers
  vector<char> Rbuf(width * height);
  vector<char> Gbuf(width * height);
  vector<char> Bbuf(width * height);

  /**
   * The input RGB file is formatted as RRRR.....GGGG....BBBB.
   * i.e the R values of all the pixels followed by the G values
   * of all the pixels followed by the B values of all pixels.
   * Hence we read the data in that order.
   */

  inputFile.read(Rbuf.data(), width * height);
  inputFile.read(Gbuf.data(), width * height);
  inputFile.read(Bbuf.data(), width * height);

  inputFile.close();

  /**
   * Allocate a buffer to store the pixel values
   * The data must be allocated with malloc(), NOT with operator new. wxWidgets
   * library requires this.
   */
  unsigned char *inData =
      (unsigned char *)malloc(width * height * 3 * sizeof(unsigned char));

  for (int i = 0; i < height * width; i++)
  {
    // We populate RGB values of each pixel in that order
    // RGB.RGB.RGB and so on for all pixels
    inData[3 * i] = Rbuf[i];
    inData[3 * i + 1] = Gbuf[i];
    inData[3 * i + 2] = Bbuf[i];
  }

  return inData;
}

void MyFrame::StartTimer(int time)
{
  m_timer.Start(time);
}

void MyFrame::SetFactors(float quantizationLevel, float deliveryMode, float latency)
{
  mQuantizationLevel = quantizationLevel;
  mDeliveryMode = deliveryMode;
  mLatency = latency;
}

void MyFrame::ExportToCSV()
{

  string filename = "Output";
  std::ofstream file(filename, std::ios::app);
  std::ofstream file2("AbsoluteSum", std::ios::app);
  std::ofstream file3("AbsoluteSum Final", std::ios::app);
  if (!file.is_open())
  {
    std::cerr << "Error opening file " << filename << std::endl;
    return;
  }
  if (!file2.is_open())
  {
    std::cerr << "Error opening file " << filename << std::endl;
    return;
  }
  if (!file3.is_open())
  {
    std::cerr << "Error opening file " << filename << std::endl;
    return;
  }
}

wxIMPLEMENT_APP(MyApp);
