/*
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; version 2 of the License.
 
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
*/

using System;


//using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using System.IO;
using System.Collections;
using Microsoft.WindowsMobile.Samples.Location;
using Microsoft.WindowsCE.Forms;

using Microsoft.WindowsMobile.Status;

namespace WMGooglemaps
{

    public partial class form1 : Form
    {
        int dispWidth, dispHeight;
        
        int zoom;   //
        int userzoom; // hodnoty: 1 = 100%,2 = 200%;
        const int ZOOM_MAX = 0;
        const int ZOOM_MIN = 17;
        const int earths_average_meridional_radius = 6367449; // [m]
        const string TILES_DIR_MENU_PREFIX = "Tiles: ";

        int tilesWidth, tilesHeight;
        ScreenOrientation orientationAtApplicationStart;

        int tilex, tiley;
        const string googlemapsRootPath = "\\Storage Card\\wmgooglemaps";
        const string missingTile = googlemapsRootPath + "\\missing.png";
        const string fileLastUsedMap = "lastmap.txt"; // getMapsRootPath() + fileLastUsedMap
        string mapDirsCurrent;
        //const string mapDirsCurrent_DEFULT = "map";
        // not implemented yeat: format of stored waypoint in pixels: ("px:",wayPointText,":",zoom.ToString(), ":", coordX.ToString(), ":", coordY.ToString(), ":", Color );
        // format of stored waypoint: ("gps:",wayPointName,":", latitude.ToString(), ":", longitude.ToString(), ":", Color );
        const string fileWayPoints = "waypoints.txt"; // is created as: getSelectedTilesPath() + "\\" + fileWayPoints
        // format of stored position: ("px:", zoom.ToString(), ":", coordX.ToString(), ":", coordY.ToString(), ":", tilesDirsCurrent);
        const string fileLastUsedPosition = "lastposition.txt"; // is created as: getSelectedTilesPath() + "\\" + fileLastUsedPosition
        string tilesDirsCurrent = "tiles";
        ArrayList tilesDirs;
        ArrayList tilesDirsMenuItems;

        int mousePosX, mousePosY; // helper vars for mouse moving the map
        int mouseDeltaX, mouseDeltaY; // helper vars promenne - how much the map was moved
        int ofsx, ofsy; // used for drawing tiles
        int coordX, coordY; // coords of the middle of the display - in pixels
        int gpscoordX, gpscoordY; // absolut coords GPS

        bool drawMouseCoord; // flag - if true => draw the box with the coords of thou mouse pointer / used for debugging
        bool flagMovingTheMouse; // flag - if true => map is being moved
        bool flagPictureBox1Click;
        bool flagDrawWayPoints;
        bool flagShowGPSCoords;
        
        bool flagStickToGPSCoords; // if true - stick the middle of the map to the GPS coords
        double gpsLatitude;
        double gpsLongitude;
        bool flagGPSLatitudeValid;
        bool flagGPSLongitudeValid;

        Bitmap bitmapBuffer = null; // buffer. used for "doubleBuffering"

        int tilesCacheSize = 64;
        Hashtable tilesCache;  // mapping String fileName - Bitmapa
        SortedList tilesTimestampCache; // mapping long timestamp - String filename
        Bitmap tileNotFound;

        private Gps gps;

        ArrayList waypoints;

        public form1()
        {
            InitializeComponent();

            this.WindowState = FormWindowState.Maximized;

            pictureBoxGPS.Visible = false;
            pictureBoxGPS.Width = 5;
            pictureBoxGPS.Height = 5;
            bgps.BackColor = System.Drawing.Color.LightGray;
            bgps.Enabled = false;
            flagStickToGPSCoords = false;

            flagDrawWayPoints = false;
            flagShowGPSCoords = false;


            gps = new Gps();

            drawMouseCoord = false;
            zoom = 9;
            userzoom = 1;
            tilesWidth = 256;
            tilesHeight = 256;

            flagPictureBox1Click = false;



            // coords of the Prague
            //coordX = (17 * 1024 + 287) * tilesWidth;
            //coordY = (10 * 1024 + 860) * tilesHeight;
            //Praha - strelecky ostrov: N50.08145, E14.4100
            // latitude N50, long E14
            // gps debug: -122.186451666; 47.6336299999
            //GPScoord_to_plaincoord(47.6336299999, -122.186451666, zoom, out coordX, out coordY); // gpsdebug - textak ze samplu od MS
            
            tilesDirsMenuItems = new ArrayList();
            tilesDirsCurrent = "";
            tilesCacheSize = 64;
            GPScoord_to_plaincoord(50.076, 14.444, zoom, out coordX, out coordY);   // praha

            waypoints = new ArrayList();
            initMap();
            
            initScreenDimensions();
            flagGPSLatitudeValid = false;
            flagGPSLongitudeValid = false;

            FileStream src = new FileStream(missingTile, FileMode.Open);
            tileNotFound = new Bitmap(src);
            src.Close();

            setbplusminusLabels();

        }

        private void initMap()
        {
            if (mapDirsCurrent == null)
            {
                readStoredMap();
            }
            else
            {
                writeMap();
            }

            readStoredPosition();
            readStoredWayPoints();
            fillTilesDirs();
            initTilesCache();
        }

        private void initTilesCache()
        {
            tilesCache = new Hashtable(tilesCacheSize);
            tilesTimestampCache = new SortedList(tilesCacheSize);
        }

        private string getMapsRootPath()
        {
            return googlemapsRootPath;
        }

        private string getSelectedMapPath()
        {
            return String.Concat(googlemapsRootPath + "\\" + mapDirsCurrent);
        }
        private string getSelectedTilesPath()
        {
            return String.Concat(googlemapsRootPath + "\\" + mapDirsCurrent + "\\" + tilesDirsCurrent);
        }

        private void initScreenDimensions()
        {
            pictureBox1.Width = this.Width;
            pictureBox1.Height = this.Height;
            dispWidth = pictureBox1.Width;
            dispHeight = pictureBox1.Height;
            if (bitmapBuffer != null)
            {
                bitmapBuffer.Dispose();
            }
            bitmapBuffer = new Bitmap(3 * dispWidth, 3 * dispHeight);
            pictureBoxGPS.Location = new System.Drawing.Point(dispWidth / 2 - 2, dispHeight / 2 - 2);

            if (SystemSettings.ScreenOrientation == ScreenOrientation.Angle0) 
            { 
                // na vysku
                bplus.Location = new System.Drawing.Point(5, dispHeight - bplus.Height - 5);
                bminus.Location = new System.Drawing.Point(1+bplus.Location.X + bplus.Width, dispHeight - bminus.Height - 5);
                buserzoom.Location = new System.Drawing.Point(1 + bminus.Location.X + bminus.Width, dispHeight - buserzoom.Height - 5);
                bgps.Location = new System.Drawing.Point(60 + buserzoom.Location.X + buserzoom.Width, dispHeight - bgps.Height - 5);
                bgpspanelswitch.Location = new System.Drawing.Point(1 + bgps.Location.X + bgps.Width, dispHeight - bgpspanelswitch.Height - 5);
            }
            else 
            {
                // na syrku
                bplus.Location = new System.Drawing.Point(dispWidth - bplus.Width - 5, 5);
                bminus.Location = new System.Drawing.Point(dispWidth - bminus.Width - 5, 1 + bplus.Location.Y + bplus.Height);
                buserzoom.Location = new System.Drawing.Point(dispWidth - buserzoom.Width - 5, 1 + bminus.Location.Y + bminus.Height);
                bgps.Location = new System.Drawing.Point(dispWidth - bgps.Width - 5, 60 + buserzoom.Location.Y + buserzoom.Height);
                bgpspanelswitch.Location = new System.Drawing.Point(dispWidth - bgpspanelswitch.Width - 5, 1 + bgps.Location.Y + bgps.Height);
            }

        }


        private void readStoredPosition()
        {
            string filepath = String.Concat( getSelectedMapPath() + "\\" + fileLastUsedPosition);
            try
            {
                // Create an instance of StreamReader to read from a file.
                // The using statement also closes the StreamReader.
                using (StreamReader sr = new StreamReader(filepath))
                {
                    String line;
                    // Read and display lines from the file until the end of 
                    // the file is reached.
                    if ((line = sr.ReadLine()) != null)
                    {
                        
                        string[] parts;
                        int cx, cy, zm;

                        parts = line.Trim().Split(':');
                        if (parts.Length != 5) throw new IOException("StoredPosition doesn't contain 5 pieces of data.");
                        if (parts[0] != "px") throw new IOException("StoredPosition px is not \'px\'.");

                        zm = Int32.Parse(parts[1]);
                        cx = Int32.Parse(parts[2]);
                        cy = Int32.Parse(parts[3]);
                        tilesDirsCurrent = parts[4];

                        // if exception was not rised:
                        coordX = cx;
                        coordY = cy;
                        zoom = zm;
                    }
                    else 
                    {
                        throw new IOException("File " + filepath + " doesn't contain data.");
                    }
                }
            }
            catch (Exception e)
            {
                // Let the user know what went wrong.
                MessageBox.Show(String.Concat("The file error: " + filepath, e.StackTrace));
            }
        }

        private void readStoredWayPoints()
        {
            waypoints = new ArrayList();
            string filepath = String.Concat(getSelectedMapPath() + "\\" + fileWayPoints);
            string waypointsList = "";
            string separator = "";
            try
            {
                // Create an instance of StreamReader to read from a file.
                // The using statement also closes the StreamReader.
                using (StreamReader sr = new StreamReader(filepath))
                {
                    String line = "";
                    // Read and display lines from the file until the end of 
                    // the file is reached.

                    // format of the stored waypoint: ("gps:",wayPointName,":", latitude.ToString(), ":", longitude.ToString(), ":", Color );
                    while ((line = sr.ReadLine()) != null)
                    {
                        try
                        {
                            if (line.Trim().Substring(0, 1).Equals("#"))
                            {
                                // mame komentar
                                continue;
                            }

                            string[] parts;
                            //int cx, cy, zm;
                            double lat, lon;
                            string name, color;

                            parts = line.Trim().Split(':');
                            if (parts.Length != 5) throw new IOException("StoredPosition doesn't contain 5 pieces of data.");
                            if (parts[0] != "gps") throw new IOException("StoredPosition gps is not \'gps\'.");

                            name = parts[1];
                            lat = Double.Parse(parts[2]);
                            lon = Double.Parse(parts[3]);
                            color = parts[4];

                            // if exception was not rised:

                            WayPoint wp = new WayPoint(name, lat, lon, color);
                            waypoints.Add(wp);

                            waypointsList = String.Concat(waypointsList, separator, name);
                            separator = ", ";

                        }
                        catch (Exception)
                        {
                            MessageBox.Show(String.Concat("readStoredWayPoints: Invalid format in line: ", line));
                        }
                    }
                }
            }
            catch (Exception e)
            {
                // Let the user know what went wrong.
                MessageBox.Show(String.Concat("The file error: " + filepath, e.StackTrace));
            }

            recountWaypointsCoords();
            if (waypoints.Count == 0)
            {
                MessageBox.Show("There are no wayps for selected map.");
            }
            else
            {
                if (waypoints.Count == 1)
                    MessageBox.Show("There is " + waypoints.Count.ToString() + " wayp. \n" + waypointsList);
                else
                    MessageBox.Show("There are " + waypoints.Count.ToString() + " wayps. \n" + waypointsList);
            }
              
        }

        private void writeMapPosition()
        {
            // save to file:
            string dirpath = String.Concat(getSelectedMapPath());
            if (Directory.Exists(dirpath))
            {
                try
                {
                    using (StreamWriter outfile =
                        new StreamWriter(dirpath + "\\" + fileLastUsedPosition))
                    {
                        string pos = string.Concat("px:", zoom.ToString(), ":", coordX.ToString(), ":", coordY.ToString(), ":", tilesDirsCurrent);
                        outfile.Write(pos);
                    }
                }
                catch (Exception exc)
                {
                    MessageBox.Show(String.Concat("Unable to store current position.\n", exc.StackTrace));
                }
            }
        }

        private void readStoredMap()
        {
            string filepath = String.Concat(getMapsRootPath() + "\\" + fileLastUsedMap);
            try
            {
                // Create an instance of StreamReader to read from a file.
                // The using statement also closes the StreamReader.
                if (!System.IO.File.Exists(filepath))
                {
                    show_dialog_select_map_dir();
                }
                else
                {
                    using (StreamReader sr = new StreamReader(filepath))
                    {
                        String line;
                        // Read and display lines from the file until the end of 
                        // the file is reached.
                        if ((line = sr.ReadLine()) != null)
                        {

                            mapDirsCurrent = line.Trim();
                            if (!Directory.Exists(getMapsRootPath() + "\\" + mapDirsCurrent))
                            {
                                //mapDirsCurrent = mapDirsCurrent_DEFULT;
                                MessageBox.Show(String.Concat("File fileLastUsedMap contains invalid map dir '" + line.Trim() + "'"));
                                show_dialog_select_map_dir();
                            }
                        }
                        else
                        {
                            throw new IOException("File " + filepath + " doesn't contain data.");
                        }
                    }
                }
            }
            catch (Exception e)
            {
                // Let the user know what went wrong.
                //mapDirsCurrent = mapDirsCurrent_DEFULT;
                MessageBox.Show(String.Concat("The file error: " + filepath, e.StackTrace));
            }
        }

        private void writeMap()
        {
            // save to file:
            string dirpath = String.Concat(getMapsRootPath());
            if (Directory.Exists(dirpath))
            {
                try
                {
                    using (StreamWriter outfile =
                        new StreamWriter(dirpath + "\\" + fileLastUsedMap))
                    {
                        string pos = string.Concat(mapDirsCurrent);
                        outfile.Write(pos);
                    }
                }
                catch (Exception exc)
                {
                    MessageBox.Show(String.Concat("Unable to store current position.\n", exc.StackTrace));
                }
            }
        }

        // fill tilesDirs 
        private void fillTilesDirs()
        {

            // remove old values
            foreach (MenuItem mi in tilesDirsMenuItems)
            {
                menuoptions.MenuItems.Remove(mi);
            }

            tilesDirs = new ArrayList(System.IO.Directory.GetDirectories( getSelectedMapPath() ));
            tilesDirsMenuItems = new ArrayList(tilesDirs.Count);
            bool dirExists = false;
            string firstDir = "";

            foreach (string s in tilesDirs)
            {
                string lastDirPart = s.Substring(s.LastIndexOf("\\") + 1);
                if (firstDir.Equals(""))
                {
                    firstDir = lastDirPart;
                }
                if (tilesDirsCurrent.Equals(lastDirPart) )
                {
                    dirExists = true;
                }

                MenuItem mi = new System.Windows.Forms.MenuItem();
                mi.Text = TILES_DIR_MENU_PREFIX + lastDirPart;
                menuoptions.MenuItems.Add(mi);
                mi.Click += new System.EventHandler(this.menuTilesDir_Click);

                tilesDirsMenuItems.Add(mi);
            }

            if (!dirExists)
            {
                tilesDirsCurrent = firstDir;
            }
        }

        private void setTilesDir(string tilesDirName)
        {
            // nastav adresar
            if (System.IO.Directory.Exists(String.Concat( getSelectedTilesPath() )))
            {
                tilesDirsCurrent = tilesDirName;
            }
            else
            {
                fillTilesDirs();
            }
            pictureBox1.Invalidate();
        }

        private int tiles_on_level(int zoom)
        {
            return 1 << (ZOOM_MIN - zoom);
        }

        /*
         * latitude - (North / South)
         * longitude - (East / West)
         */
        private void GPScoord_to_plaincoord(double latitude, double longitude, int zoom, out int coordx, out int coordy)
        {
            int world_pixels = tiles_on_level(zoom) * tilesWidth;
            coordx = (int)Math.Round((world_pixels * (longitude + 180) / 360.0));

            double pixels_per_radian = world_pixels / (2 * Math.PI);
            double e = Math.Sin(latitude * (Math.PI / 180));
            coordy = (int)Math.Round((world_pixels / 2 + 0.5 * Math.Log((1 + e) / (1 - e)) * (-pixels_per_radian)));

        }

        private double GPSTileWidth_to_metres()
        {
            double lat, lon;
            GPSplaincoord_to_coord(coordX, coordY, zoom, out lat, out lon);

            // count the length of tile in coordY in meters
            
            //double metersInDegree = Meters * Math.PI * Math.Cos(lat * Math.PI / 180) / 180;
            return earths_average_meridional_radius * Math.Cos(lat * Math.PI / 180) * 2 * Math.PI / (double)tiles_on_level(zoom);
            //return metersInTile;
        }

        private void GPSplaincoord_to_coord(int coordx, int coordy, int zoom, out double latitude, out double longitude)
        { 
            int worldPixels = tiles_on_level(zoom) * tilesWidth;
            double x = coordx * 2.0 / worldPixels - 1;
            double y = coordy * 2.0 / worldPixels - 1;

            longitude = x * 180;
            y = Math.Exp(-y * 2 * Math.PI);
            double e = (y-1)/(y+1);
            latitude = 180/Math.PI * Math.Asin(e);
        }


        private void Form1_Load(object sender, EventArgs e)
        {
            //MessageBox.Show("Here we go!");
        }

        private void menuClose_Click(object sender, EventArgs e)
        {
            if (gps.Opened)
            {
                gps.DeviceStateChanged -= gps_DeviceStateChanged;
                gps.LocationChanged -= gps_LocationChanged;

                gps.Close();
            }

            writeMapPosition();

            Close();
        }

        private Bitmap getTile( int lzoom, int ltilex, int ltiley )
        {
            int xmaj = (ltilex) / 1024;
            int xmin = (ltilex) % 1024;
            int ymaj = (ltiley) / 1024;
            int ymin = (ltiley) % 1024;

            string tileFileName = String.Concat(getSelectedTilesPath(), "\\", lzoom.ToString(), "\\",
                            xmaj.ToString(), "\\", xmin.ToString(), "\\",
                            ymaj.ToString(), "\\", ymin.ToString(), ".png");

            if (tilesCache.ContainsKey(tileFileName))
            {
                // use kay and set new timestamp for it
                long tstamp = DateTime.Now.ToFileTime();
                int idx = tilesTimestampCache.IndexOfValue(tileFileName);
                tilesTimestampCache.RemoveAt(idx);
                // is my timestamp newer than timestamp in the array?
                if ((tilesTimestampCache.Count > 0) && (tstamp <= (long)tilesTimestampCache.GetKey(tilesTimestampCache.Count - 1)))
                {
                    tstamp = (long)tilesTimestampCache.GetKey(tilesTimestampCache.Count - 1) + 1;
                }
                tilesTimestampCache.Add(tstamp, tileFileName);

                return (Bitmap)tilesCache[tileFileName];
            }
            else
            {
                if (!File.Exists(tileFileName))
                {
                    return tileNotFound;
                }
                else
                {
                    FileStream src = new FileStream(tileFileName, FileMode.Open);
                    Bitmap btm = new Bitmap(src);
                    src.Close();

                    if (tilesTimestampCache.Count >= tilesCacheSize)
                    {
                        // tha cache is full - delete the tile used the least
                        String tileToRemove = (String)tilesTimestampCache.GetByIndex(0);
                        tilesTimestampCache.RemoveAt(0);
                        tilesCache.Remove(tileToRemove);
                    }

                    long tstamp = DateTime.Now.ToFileTime();
                    // je muj timestamp novejsi nez nejnovejsi v poli?
                    if ((tilesTimestampCache.Count > 0) && (tstamp <= (long)tilesTimestampCache.GetKey(tilesTimestampCache.Count - 1)))
                    {
                        tstamp = (long)tilesTimestampCache.GetKey(tilesTimestampCache.Count - 1) + 1;
                    }
                    tilesTimestampCache.Add(tstamp, tileFileName);
                    tilesCache.Add(tileFileName, btm);

                    return btm;
                }
            }
        }

        private void CoordToTileAndOffeset()
        {
            int coMajX, coMinX, coMajY, coMinY;

            int startX = coordX - dispWidth / 2;
            coMajX = startX / tilesWidth;
            coMinX = startX % tilesWidth;

            tilex = coMajX;
            ofsx = -1 * (coMinX);


            int startY = coordY - dispHeight / 2;
            coMajY = startY / tilesWidth;
            coMinY = startY % tilesWidth;

            tiley = coMajY;
            ofsy = -1 * (coMinY);


            return;
        }

        private void drawWayPoints(Graphics g)
        {
            // do we have to draw wayPoints?
            if (!flagDrawWayPoints)
                return;

            foreach (WayPoint wp in waypoints)
            {
                if (wp.px > (coordX - dispWidth / userzoom) && wp.px < (coordX + dispWidth / userzoom) &&
                    wp.py > (coordY - dispHeight / userzoom) && wp.py < (coordY + dispHeight / userzoom))
                {
                    // i can draw, draw
                    g.FillRectangle(new SolidBrush(wp.color), wp.px - coordX + dispWidth / 2 - wp.size/2, wp.py - coordY + dispHeight / 2 - wp.size / 2, wp.size, wp.size);
                    // drow waypoint name
                    g.DrawString(wp.name, new Font("Arial", 7, System.Drawing.FontStyle.Regular), new SolidBrush(wp.color), wp.px - coordX + dispWidth / 2 + wp.size / 2 + 10, wp.py - coordY + dispHeight / 2 - 12);
                }
            }
            
        }

        private void pictureBox1_Paint(object sender, PaintEventArgs e)
        {
            int countx = 0;
            int county = 0;

            // draw tiles
            Graphics g = e.Graphics;

            if (!flagMovingTheMouse)
            {
                CoordToTileAndOffeset();
                Graphics gBuffer = Graphics.FromImage(bitmapBuffer);
                do
                {
                    // do horizontal tiles
                    do
                    {
                        Bitmap tle = getTile(zoom, tilex + countx, tiley + county);
                        gBuffer.DrawImage(tle, tilesWidth * countx + ofsx + dispWidth, tilesHeight * county + ofsy + dispHeight);
                        countx += 1;
                    } while ((countx * tilesWidth + ofsx) < pictureBox1.Width);

                    countx = 0;
                    county += 1;
                } while ((county * tilesHeight + ofsy) < pictureBox1.Height);
                gBuffer.Dispose();

                mouseDeltaX = 0;
                mouseDeltaY = 0;

                if (flagShowGPSCoords)
                {
                    double lat, lon;
                    GPSplaincoord_to_coord(coordX, coordY, zoom, out lat, out lon);
                    lat = Math.Round(lat, 4);
                    lon = Math.Round(lon, 4);
                    string latlon = lat.ToString() + ", " + lon.ToString();
                    g.FillRectangle(new SolidBrush(Color.Red), dispWidth / 2 - 3, dispHeight / 2, 6, 1);
                    g.FillRectangle(new SolidBrush(Color.Red), dispWidth / 2, dispHeight / 2 - 3, 1, 6);
                    g.DrawString(latlon, new Font("Arial", 8, System.Drawing.FontStyle.Bold), new SolidBrush(Color.Red), dispWidth / 2 + 8, dispHeight / 2 - 13);
                }

            }

            // draw meritko
            if (userzoom == 1)
            {
                Rectangle srcRect = new Rectangle(dispWidth + mouseDeltaX, dispHeight + mouseDeltaY, dispWidth, dispHeight);
                g.DrawImage(bitmapBuffer, 0, 0, srcRect, GraphicsUnit.Pixel);
                
            }
            else
            {
                Rectangle dstRect = new Rectangle(0, 0, dispWidth, dispHeight);
                // userzoom = 2
                // dispWidth is divided by 4, I want to get quartre to the edge of the display
                // the same for dispHeight
                Rectangle srcRect = new Rectangle(dispWidth + dispWidth / 4 + mouseDeltaX / 2, dispHeight + dispHeight / 4 + mouseDeltaY / 2, dispWidth / 2, dispHeight / 2);
                g.DrawImage(bitmapBuffer, dstRect, srcRect, GraphicsUnit.Pixel);
            }

            // finalni dokresleni:
            if (!flagMovingTheMouse)
            {
                g.FillRectangle(new SolidBrush(Color.Red), 5, 16, tilesWidth, 4);
                g.FillRectangle(new SolidBrush(Color.Black), 5, 12, 2, 10);
                g.FillRectangle(new SolidBrush(Color.Black), 5 + tilesWidth / 2, 14, 2, 6);
                g.FillRectangle(new SolidBrush(Color.Black), 5 + tilesWidth, 12, 2, 10);
                g.DrawString(String.Concat(Math.Round(GPSTileWidth_to_metres() / userzoom).ToString(), " m"), new Font("Arial", 10, System.Drawing.FontStyle.Bold), new SolidBrush(Color.Red), 5 + tilesWidth + 10, 2);

                if (flagShowGPSCoords)
                {
                    double lat, lon;
                    GPSplaincoord_to_coord(coordX, coordY, zoom, out lat, out lon);
                    lat = Math.Round(lat, 4);
                    lon = Math.Round(lon, 4);
                    string latlon = lat.ToString() + ", " + lon.ToString();
                    g.FillRectangle(new SolidBrush(Color.DarkRed), dispWidth / 2 - 3, dispHeight / 2, 6, 1);
                    g.FillRectangle(new SolidBrush(Color.DarkRed), dispWidth / 2, dispHeight / 2 - 3, 1, 6);
                    g.DrawString(latlon, new Font("Arial", 10, System.Drawing.FontStyle.Bold), new SolidBrush(Color.Red), dispWidth / 2 + 8, dispHeight / 2 - 13);
                }
            }



            // draw wayPoints
            drawWayPoints(g);



            if (drawMouseCoord)
            {
                g.FillRectangle(new SolidBrush(Color.White), new Rectangle(0, 0, 200, 200));
                //string outStr = String.Concat("l:",left.ToString(),":t:",top.ToString(),":w:",width.ToString(),":h:",height.ToString());
                string outStr = String.Concat("mPX:", mousePosX.ToString(), ": mPY:", mousePosY.ToString(), ": mDX:", mouseDeltaX.ToString(), ": mDY:", mouseDeltaY.ToString());
                g.DrawString(outStr,
                    new Font("Arial", 10, FontStyle.Regular), new System.Drawing.SolidBrush(Color.Black), new RectangleF(0, 0, 200, 100));

                drawMouseCoord = false;
            }

            // e.ClipRectangle : Rectangle
            // e.Graphics : Graphics
        }

        private void pictureBox1_MouseMove(object sender, MouseEventArgs e)
        {
            mouseDeltaX = mousePosX - e.X;
            mouseDeltaY = mousePosY - e.Y;

            flagMovingTheMouse = true;
            pictureBoxGPS.Visible = false;
            pictureBox1.Invalidate();
        }

        private void pictureBox1_MouseDown(object sender, MouseEventArgs e)
        {
            mousePosX = e.X;
            mousePosY = e.Y;

            //System.Console.WriteLine("mouseDown");
        }

        private void pictureBox1_MouseUp(object sender, MouseEventArgs e)
        {
            mouseDeltaX = mousePosX - e.X;
            mouseDeltaY = mousePosY - e.Y;
            coordX += mouseDeltaX / userzoom;   // to je divne. userzoom se pouziva tady a v onPain. Melo by to byt jen na jedinem miste
            coordY += mouseDeltaY / userzoom;

            if (flagPictureBox1Click)
            {
                // clicked point should be moved to the middle of the display
                // click: e.X, e.Y (0 - dispWidth, 0 - dispHeight)
                // old middle point = dispWidth / 2; dispHeight / 2 ~ coordX, coordY
                // new middle point: delta = e.X - dispWidth / 2
                if (Math.Abs(mouseDeltaX) < 10 && Math.Abs(mouseDeltaY) < 10)
                {
                    coordX += (e.X - dispWidth / 2) / userzoom;   // to je divne. userzoom se pouziva tady a v onPain. Melo by to byt jen na jedinem miste
                    coordY += (e.Y - dispHeight / 2) / userzoom;
                }
                flagPictureBox1Click = false;
            }
            /*
            mousePosX = e.X;
            mousePosY = e.Y;
             */
            //drawMouseCoord = true;
            flagMovingTheMouse = false;
            pictureBox1.Invalidate();

            //System.Console.WriteLine("mouseUp");

        }

        private void incrementZoom()
        {
            // zoom in
            zoom--;
            coordX *= 2;
            coordY *= 2;
        }
        private void decrementZoom()
        {
            // zoom out
            zoom++;
            coordX = (int)Math.Round(coordX / 2.0);
            coordY = (int)Math.Round(coordY / 2.0);
        }

        private void setbplusminusLabels()
        {
            int v;
            v = zoom - 1;
            bplus.Text = zoom.ToString() + "+";
            v = zoom + 1;
            bminus.Text = zoom.ToString() + "-";
        }

        /*
        private void changeZoom(int newZoom)
        {
            / *
             *  z3 = 2*z4 = 2*2*z5 = z5 * 2^(z5-z3)
             *  newCoord = coord * 2^(zoom - newZoom);
             * /
            int newCoordx;
            int newCoordy;

            if (newZoom > zoom)
            {
                // shrinking the display
                newCoordx = coordX / 2 ^ (newZoom - zoom);
                newCoordy = coordY / 2 ^ (newZoom - zoom);
            }
            else
            {
                // mame priblizenii
                newCoordx = coordX * 2 ^ (zoom - newZoom);
                newCoordy = coordY * 2 ^ (zoom - newZoom);
            }

            zoom = newZoom;
            coordX = newCoordx;
            coordY = newCoordy;
            pictureBox1.Invalidate();
        }
         */

        private void recountWaypointsCoords()
        {
            foreach (WayPoint wp in waypoints)
            {
                GPScoord_to_plaincoord(wp.latitude, wp.longitude, zoom, out wp.px, out wp.py);
            }
        }

        private void bplus_Click(object sender, EventArgs e)
        {
            if (zoom > ZOOM_MAX)
            {
                //changeZoom(zoom - 1);
                incrementZoom();
            }
            setbplusminusLabels();
            recountWaypointsCoords();
            pictureBox1.Focus();
            pictureBox1.Invalidate();
        }

        private void bminus_Click(object sender, EventArgs e)
        {
            if (zoom < ZOOM_MIN)
            {
                //changeZoom(zoom + 1);
                decrementZoom();
            }

            setbplusminusLabels();
            recountWaypointsCoords();
            pictureBox1.Focus();
            pictureBox1.Invalidate();
        }

        private void 
            buserzoom_Click(object sender, EventArgs e)
        {
            if (userzoom == 1)
            {
                userzoom = 2;
                buserzoom.Text = "O";
            }
            else
            {
                userzoom = 1;
                buserzoom.Text = "o";
            }
            pictureBox1.Focus();
            pictureBox1.Invalidate();
        }

        private void pictureBox1_Click(object sender, EventArgs e)
        {
            // go to the coords
            // order - set flag we have the click - is used in mouseUp
            // order: MDown, MMove, MClick, Mup
            flagPictureBox1Click = true;
        }

        private void pictureBox1_DoubleClick(object sender, EventArgs e)
        {
            // go to the coords and zoom + 1
            // set flag we have double click - is used in mouseUp
            incrementZoom();
        }

        private void gpsStickToMapChange()
        {
            if (!flagStickToGPSCoords)
            {
                if (flagGPSLongitudeValid && flagGPSLongitudeValid)
                {
                    // zobraz stred
                    pictureBoxGPS.Visible = true;
                    flagStickToGPSCoords = true;
                    pictureBoxGPSchangeColor();
                    return;
                }
            }

            // hide the middle
            pictureBoxGPS.Visible = false;
            flagStickToGPSCoords = false;
            pictureBoxGPSchangeColor();
            return;
        }

        private void bgps_Click(object sender, EventArgs e)
        {
            gpsStickToMapChange();
        }

        /*
            GPS stavy:
            - gps off: enable=false
            - gps on: enable = true

            StickToGPS:
            - blue

            Latitude&Longitude valid:
            - light blue

            else:
            - light gray
         */
        private void pictureBoxGPSchangeColor()
        {

            if (!bgps.Enabled)
            {
                bgps.BackColor = System.Drawing.Color.LightGray;
                return;
            }
            if (flagGPSLatitudeValid && flagGPSLongitudeValid)
            {
                if (flagStickToGPSCoords)
                {
                    bgps.BackColor = System.Drawing.Color.Blue;
                }
                else
                {
                    bgps.BackColor = System.Drawing.Color.LightBlue;
                }
            }
            else
            {
                bgps.BackColor = System.Drawing.Color.LightGray;
            }
            return;
        }

        void gps_LocationChanged(object sender, LocationChangedEventArgs args)
        {
            ControlUpdater cu = UpdateControl;
            ControlUpdaterGPS cugps = UpdateControlGPS;

            GpsPosition position = args.Position;

            if (position.LatitudeValid)
            {
                Invoke(cugps, 0, position.Latitude);
                Invoke(cu, tbLatitude, position.Latitude.ToString());
            }
            if (position.LongitudeValid) 
            {
                Invoke(cugps, 1, position.Longitude);
                Invoke(cu, tbLongitude, position.Longitude.ToString());
            }
            if (position.HeadingValid)
                Invoke(cu, tbHeading, position.Heading.ToString());
            if (position.SatellitesInViewCountValid)
                Invoke(cu, tbSatellites, position.SatellitesInViewCount.ToString());
        }

        void gps_DeviceStateChanged(object sender, DeviceStateChangedEventArgs args)
        {
            ControlUpdater cu = UpdateControl;

            GpsDeviceState device = args.DeviceState;

            Invoke(cu, tbGPSDevice, device.FriendlyName);
            Invoke(cu, tbGPSDeviceState, device.DeviceState.ToString());
            Invoke(cu, tbGPSServiceState, device.ServiceState.ToString());
        }

        private delegate void ControlUpdater(Control c, string s);
        private delegate void ControlUpdaterGPS(int latlong, double value);

        private void UpdateControl(Control c, string s)
        {
            c.Text = s;
        }

        private void UpdateControlGPS(int latlong, double value)
        {
            if (latlong == 0)
            {
                // latitude
                gpsLatitude = value;
                flagGPSLatitudeValid = true;
            }
            else
            {
                // longitude
                gpsLongitude = value;
                flagGPSLongitudeValid = true;
            }

            if (flagGPSLatitudeValid && flagGPSLongitudeValid)
            {
                if (flagStickToGPSCoords)
                {
                    int cx, cy;
                    GPScoord_to_plaincoord(gpsLatitude, gpsLongitude, zoom, out cx, out cy);
                    if ((Math.Round(Math.Sqrt((cx - coordX) * (cx - coordX) + (cy - coordY) * (cy - coordY))) > 2) || (pictureBoxGPS.Visible == false))
                    {
                        coordX = cx;
                        coordY = cy;
                        pictureBoxGPS.Visible = true;
                        pictureBox1.Invalidate();
                    }
                }
                else
                {
                    pictureBoxGPSchangeColor();
                }
            }
        }


        // it's general handler when tiles directory is changed in the menu
        private void menuTilesDir_Click(object sender, EventArgs e)
        {
            setTilesDir(((MenuItem)sender).Text.Substring(TILES_DIR_MENU_PREFIX.Length));
        }


        private void menugps_Click(object sender, EventArgs e)
        {

            if (!gps.Opened)
            {
                gps.DeviceStateChanged += new DeviceStateChangedEventHandler(gps_DeviceStateChanged);
                gps.LocationChanged += new LocationChangedEventHandler(gps_LocationChanged);
                gps.Open();

                bgps.Enabled = true;
                pictureBoxGPSchangeColor();
            }
            else
            {
                gps.DeviceStateChanged -= gps_DeviceStateChanged;
                gps.LocationChanged -= gps_LocationChanged;
                gps.Close();
                
                tbGPSDevice.Text = "";
                tbGPSDeviceState.Text = "";
                tbGPSServiceState.Text = "";
                tbHeading.Text = "";
                tbLatitude.Text = "";
                tbLongitude.Text = "";
                tbSatellites.Text = "";

                bgps.Enabled = false;
                flagGPSLatitudeValid = false;
                flagGPSLongitudeValid = false;
                pictureBoxGPSchangeColor();
            }
            menugps.Text = gps.Opened ? "Switch GPS Off" : "Switch GPS On";
        }

        private void bgpspanelswitch_Click(object sender, EventArgs e)
        {
            // hide and show gps panel
            if (panelGPSDetails.Visible)
            {
                panelGPSDetails.Visible = false;
                //menugps.Text = "Switch GPS On";
            }
            else
            {
                panelGPSDetails.Visible = true;
                //menugps.Text = "Switch GPS Off";
            }
        }

        private void form1_KeyDown(object sender, KeyEventArgs e)
        {

        }

        private void menuScreenOrientation_Click(object sender, EventArgs e)
        {
            if (SystemSettings.ScreenOrientation == ScreenOrientation.Angle0)
            {
                SystemSettings.ScreenOrientation = ScreenOrientation.Angle270;
            }
            else
            {
                SystemSettings.ScreenOrientation = ScreenOrientation.Angle0;
            }
            initScreenDimensions();
            pictureBox1.Invalidate();
        }

        private void form1_Activated(object sender, EventArgs e)
        {
            orientationAtApplicationStart = SystemSettings.ScreenOrientation;
        }

        private void form1_Deactivate(object sender, EventArgs e)
        {
            SystemSettings.ScreenOrientation = orientationAtApplicationStart;
        }

        private void show_dialog_select_map_dir()
        {
            int xofs = 10;
            int yofs = 20;


            ArrayList mapDirs = new ArrayList(System.IO.Directory.GetDirectories(getMapsRootPath()));
            //ArrayList mapDirsMenuItems = new ArrayList(mapDirs.Count);
            bool dirExists = false;
            string firstDir = "";

            int index = 0;
            int space = 41;
            int btnheight = 30;
            foreach (string s in mapDirs)
            {
                string lastDirPart = s.Substring(s.LastIndexOf("\\") + 1);

                Button btn = new System.Windows.Forms.Button();
                btn.Location = new Point(xofs, yofs + index * space);
                btn.Width = panelSelectMap.Width - 20;
                btn.Height = btnheight;

                btn.Text = lastDirPart;
                panelSelectMap.Controls.Add(btn);
                btn.Click += new System.EventHandler(this.panelSelectMapButton_Click);

                index++;
            }

            panelSelectMap.Visible = true;
        }

        private void menuItem1_Click(object sender, EventArgs e)
        {
            show_dialog_select_map_dir();
        }

        private void panelSelectMapButton_Click(object sender, EventArgs e)
        {
            if (mapDirsCurrent == null || !mapDirsCurrent.Equals(((Control)sender).Text))
            {
                if (flagStickToGPSCoords)
                {
                    gpsStickToMapChange();
                }
                this.Text = mapDirsCurrent;
                writeMapPosition();
                mapDirsCurrent = ((Control)sender).Text;
                panelSelectMap.Visible = false;
                initMap();
                pictureBox1.Invalidate();
            }
        }

        private void bmapsCancel_Click(object sender, EventArgs e)
        {
            //skryj
            panelSelectMap.Visible = false;

        }

        private void menuwps_Click(object sender, EventArgs e)
        {
            if (flagDrawWayPoints)
            {
                flagDrawWayPoints = false;
                menuwps.Text = "Show WayPs";
            }
            else
            {
                flagDrawWayPoints = true;
                menuwps.Text = "Hide WayPs";
            }
            pictureBox1.Invalidate();
        }

        private void menuShowGPSCoords_Click(object sender, EventArgs e)
        {
            if (flagShowGPSCoords)
            {
                flagShowGPSCoords = false;
                menuShowGPSCoords.Text = "Show GPS coords";
            }
            else
            {
                flagShowGPSCoords = true;
                menuShowGPSCoords.Text = "Hide GPS coords";
            }
            pictureBox1.Invalidate();
        }
    }

    public class WayPoint
    {
        public double latitude, longitude;
        public int zoom, px, py;
        public string name;
        public Color color;

        public int size;

        public void setSize( int s )
        {
            size = s;
        }
        public int getSize()
        {
            return size;
        }
        public int getpx()
        {
            return px;
        }
        public int getpy()
        {
            return py;
        }
        public Color getColor()
        {
            return color;
        }
        public void setpx(int x)
        {
            px = x;
        }
        public void getpy(int y)
        {
            py = y;
        }

        public WayPoint(string aname, double alat, double alon, string acolor)
        {
            size = 2;
            latitude = alat;
            longitude = alon;
            name = aname;
            if (acolor.Equals("black"))
                color = Color.Black;
            else if (acolor.Equals("yellow"))
                color = Color.Yellow;
            else if (acolor.Equals("green"))
                color = Color.Green;
            else if (acolor.Equals("cyan"))
                color = Color.Cyan;
            else if (acolor.Equals("magenta"))
                color = Color.Magenta;
            else if (acolor.Equals("orange"))
                color = Color.Orange;
            else if (acolor.Equals("red"))
                color = Color.Red;
            else if (acolor.Equals("white"))
                color = Color.White;
            else if (acolor.Equals("blue"))
                color = Color.Blue;
            else
                color = Color.Black;
        }
    }



}