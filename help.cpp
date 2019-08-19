// https://stackoverflow.com/questions/31568829/how-to-extract-lines-from-each-contour-in-opencv-for-android
#include <opencv2/opencv.hpp>
using namespace cv;
using namespace std;

int main()
{
    RNG rng(12345);
    Mat3b img = imread("path_to_image");
    Mat1b gray;
    cvtColor(img, gray, COLOR_BGR2GRAY);

    Mat3b result;
    cvtColor(gray, result, COLOR_GRAY2BGR);

    // Detect lines
    Ptr<LineSegmentDetector> detector = createLineSegmentDetector();
    vector<Vec4i> lines;
    detector->detect(gray, lines);

    // Draw lines
    Mat1b lineMask(gray.size(), uchar(0));
    for (int i = 0; i < lines.size(); ++i)
    {
        line(lineMask, Point(lines[i][0], lines[i][1]), Point(lines[i][2], lines[i][3]), Scalar(255), 2);
    }

    // Compute edges
    Mat1b edges;
    Canny(gray, edges, 200, 400);

    // Find contours
    vector<vector<Point>> contours;
    findContours(edges.clone(), contours, CV_RETR_EXTERNAL, CV_CHAIN_APPROX_NONE);

    for (int i = 0; i < contours.size(); ++i)
    {
        // Draw each contour
        Mat1b contourMask(gray.size(), uchar(0));
        drawContours(contourMask, contours, i, Scalar(255), 2); // Better use 1 here. 2 is just for visualization purposes

        // AND the contour and the lines
        Mat1b bor;
        bitwise_and(contourMask, lineMask, bor);

        // Draw the common pixels with a random color
        vector<Point> common;
        findNonZero(bor, common);

        Vec3b color = Vec3b(rng.uniform(0, 255), rng.uniform(0, 255), rng.uniform(0, 255));
        for (int j = 0; j < common.size(); ++j)
        {
            result(common[j]) = color;
        }
    }


    imshow("result", result);
    waitKey();

    return 0;
}