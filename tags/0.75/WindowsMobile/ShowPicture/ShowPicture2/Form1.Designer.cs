/*
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; version 2 of the License.
 
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
*/
namespace WMGooglemaps
{
    partial class form1
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;
        private System.Windows.Forms.MainMenu mainMenu1;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.mainMenu1 = new System.Windows.Forms.MainMenu();
            this.menuClose = new System.Windows.Forms.MenuItem();
            this.menuoptions = new System.Windows.Forms.MenuItem();
            this.menugps = new System.Windows.Forms.MenuItem();
            this.menuShowGPSCoords = new System.Windows.Forms.MenuItem();
            this.menuSelectMap = new System.Windows.Forms.MenuItem();
            this.menuwps = new System.Windows.Forms.MenuItem();
            this.menuScreenOrientation = new System.Windows.Forms.MenuItem();
            this.pictureBox1 = new System.Windows.Forms.PictureBox();
            this.bplus = new System.Windows.Forms.Button();
            this.bminus = new System.Windows.Forms.Button();
            this.buserzoom = new System.Windows.Forms.Button();
            this.bgps = new System.Windows.Forms.Button();
            this.pictureBoxGPS = new System.Windows.Forms.PictureBox();
            this.panelGPSDetails = new System.Windows.Forms.Panel();
            this.ltbSatellites = new System.Windows.Forms.Label();
            this.ltbLongitude = new System.Windows.Forms.Label();
            this.ltbLatitude = new System.Windows.Forms.Label();
            this.ltbHeading = new System.Windows.Forms.Label();
            this.ltbGPSServiceState = new System.Windows.Forms.Label();
            this.ltbGPSDeviceState = new System.Windows.Forms.Label();
            this.ltbGPSDevice = new System.Windows.Forms.Label();
            this.tbSatellites = new System.Windows.Forms.TextBox();
            this.tbLongitude = new System.Windows.Forms.TextBox();
            this.tbLatitude = new System.Windows.Forms.TextBox();
            this.tbHeading = new System.Windows.Forms.TextBox();
            this.tbGPSServiceState = new System.Windows.Forms.TextBox();
            this.tbGPSDeviceState = new System.Windows.Forms.TextBox();
            this.tbGPSDevice = new System.Windows.Forms.TextBox();
            this.bgpspanelswitch = new System.Windows.Forms.Button();
            this.panelSelectMap = new System.Windows.Forms.Panel();
            this.bmapsCancel = new System.Windows.Forms.Button();
            this.panelGPSDetails.SuspendLayout();
            this.panelSelectMap.SuspendLayout();
            this.SuspendLayout();
            // 
            // mainMenu1
            // 
            this.mainMenu1.MenuItems.Add(this.menuClose);
            this.mainMenu1.MenuItems.Add(this.menuoptions);
            // 
            // menuClose
            // 
            this.menuClose.Text = "Close";
            this.menuClose.Click += new System.EventHandler(this.menuClose_Click);
            // 
            // menuoptions
            // 
            this.menuoptions.MenuItems.Add(this.menugps);
            this.menuoptions.MenuItems.Add(this.menuShowGPSCoords);
            this.menuoptions.MenuItems.Add(this.menuSelectMap);
            this.menuoptions.MenuItems.Add(this.menuwps);
            this.menuoptions.MenuItems.Add(this.menuScreenOrientation);
            this.menuoptions.Text = "Options";
            // 
            // menugps
            // 
            this.menugps.Text = "Switch GPS On";
            this.menugps.Click += new System.EventHandler(this.menugps_Click);
            // 
            // menuShowGPSCoords
            // 
            this.menuShowGPSCoords.Text = "Show GPS coords";
            this.menuShowGPSCoords.Click += new System.EventHandler(this.menuShowGPSCoords_Click);
            // 
            // menuSelectMap
            // 
            this.menuSelectMap.Text = "Select map";
            this.menuSelectMap.Click += new System.EventHandler(this.menuItem1_Click);
            // 
            // menuwps
            // 
            this.menuwps.Text = "Show WayPs";
            this.menuwps.Click += new System.EventHandler(this.menuwps_Click);
            // 
            // menuScreenOrientation
            // 
            this.menuScreenOrientation.Text = "Landscape / Portrait";
            this.menuScreenOrientation.Click += new System.EventHandler(this.menuScreenOrientation_Click);
            // 
            // pictureBox1
            // 
            this.pictureBox1.Location = new System.Drawing.Point(0, 0);
            this.pictureBox1.Name = "pictureBox1";
            this.pictureBox1.Size = new System.Drawing.Size(240, 268);
            this.pictureBox1.DoubleClick += new System.EventHandler(this.pictureBox1_DoubleClick);
            this.pictureBox1.MouseMove += new System.Windows.Forms.MouseEventHandler(this.pictureBox1_MouseMove);
            this.pictureBox1.Click += new System.EventHandler(this.pictureBox1_Click);
            this.pictureBox1.MouseDown += new System.Windows.Forms.MouseEventHandler(this.pictureBox1_MouseDown);
            this.pictureBox1.Paint += new System.Windows.Forms.PaintEventHandler(this.pictureBox1_Paint);
            this.pictureBox1.MouseUp += new System.Windows.Forms.MouseEventHandler(this.pictureBox1_MouseUp);
            // 
            // bplus
            // 
            this.bplus.Location = new System.Drawing.Point(10, 9);
            this.bplus.Name = "bplus";
            this.bplus.Size = new System.Drawing.Size(30, 30);
            this.bplus.TabIndex = 1;
            this.bplus.Text = "+";
            this.bplus.Click += new System.EventHandler(this.bplus_Click);
            // 
            // bminus
            // 
            this.bminus.Location = new System.Drawing.Point(41, 9);
            this.bminus.Name = "bminus";
            this.bminus.Size = new System.Drawing.Size(30, 30);
            this.bminus.TabIndex = 2;
            this.bminus.Text = "-";
            this.bminus.Click += new System.EventHandler(this.bminus_Click);
            // 
            // buserzoom
            // 
            this.buserzoom.Location = new System.Drawing.Point(72, 9);
            this.buserzoom.Name = "buserzoom";
            this.buserzoom.Size = new System.Drawing.Size(30, 30);
            this.buserzoom.TabIndex = 4;
            this.buserzoom.Text = "o";
            this.buserzoom.Click += new System.EventHandler(this.buserzoom_Click);
            // 
            // bgps
            // 
            this.bgps.BackColor = System.Drawing.Color.Blue;
            this.bgps.Location = new System.Drawing.Point(152, 9);
            this.bgps.Name = "bgps";
            this.bgps.Size = new System.Drawing.Size(30, 30);
            this.bgps.TabIndex = 6;
            this.bgps.Text = "G";
            this.bgps.Click += new System.EventHandler(this.bgps_Click);
            // 
            // pictureBoxGPS
            // 
            this.pictureBoxGPS.BackColor = System.Drawing.Color.MediumBlue;
            this.pictureBoxGPS.Location = new System.Drawing.Point(103, 9);
            this.pictureBoxGPS.Name = "pictureBoxGPS";
            this.pictureBoxGPS.Size = new System.Drawing.Size(15, 14);
            // 
            // panelGPSDetails
            // 
            this.panelGPSDetails.Controls.Add(this.ltbSatellites);
            this.panelGPSDetails.Controls.Add(this.ltbLongitude);
            this.panelGPSDetails.Controls.Add(this.ltbLatitude);
            this.panelGPSDetails.Controls.Add(this.ltbHeading);
            this.panelGPSDetails.Controls.Add(this.ltbGPSServiceState);
            this.panelGPSDetails.Controls.Add(this.ltbGPSDeviceState);
            this.panelGPSDetails.Controls.Add(this.ltbGPSDevice);
            this.panelGPSDetails.Controls.Add(this.tbSatellites);
            this.panelGPSDetails.Controls.Add(this.tbLongitude);
            this.panelGPSDetails.Controls.Add(this.tbLatitude);
            this.panelGPSDetails.Controls.Add(this.tbHeading);
            this.panelGPSDetails.Controls.Add(this.tbGPSServiceState);
            this.panelGPSDetails.Controls.Add(this.tbGPSDeviceState);
            this.panelGPSDetails.Controls.Add(this.tbGPSDevice);
            this.panelGPSDetails.Location = new System.Drawing.Point(10, 40);
            this.panelGPSDetails.Name = "panelGPSDetails";
            this.panelGPSDetails.Size = new System.Drawing.Size(217, 225);
            this.panelGPSDetails.Visible = false;
            // 
            // ltbSatellites
            // 
            this.ltbSatellites.Location = new System.Drawing.Point(8, 199);
            this.ltbSatellites.Name = "ltbSatellites";
            this.ltbSatellites.Size = new System.Drawing.Size(100, 20);
            this.ltbSatellites.Text = "tbSatellites";
            // 
            // ltbLongitude
            // 
            this.ltbLongitude.Location = new System.Drawing.Point(8, 171);
            this.ltbLongitude.Name = "ltbLongitude";
            this.ltbLongitude.Size = new System.Drawing.Size(100, 20);
            this.ltbLongitude.Text = "tbLongitude";
            // 
            // ltbLatitude
            // 
            this.ltbLatitude.Location = new System.Drawing.Point(8, 143);
            this.ltbLatitude.Name = "ltbLatitude";
            this.ltbLatitude.Size = new System.Drawing.Size(100, 20);
            this.ltbLatitude.Text = "tbLatitude";
            // 
            // ltbHeading
            // 
            this.ltbHeading.Location = new System.Drawing.Point(8, 115);
            this.ltbHeading.Name = "ltbHeading";
            this.ltbHeading.Size = new System.Drawing.Size(100, 20);
            this.ltbHeading.Text = "tbHeading";
            // 
            // ltbGPSServiceState
            // 
            this.ltbGPSServiceState.Location = new System.Drawing.Point(8, 66);
            this.ltbGPSServiceState.Name = "ltbGPSServiceState";
            this.ltbGPSServiceState.Size = new System.Drawing.Size(100, 20);
            this.ltbGPSServiceState.Text = "tbGPSServiceState";
            // 
            // ltbGPSDeviceState
            // 
            this.ltbGPSDeviceState.Location = new System.Drawing.Point(8, 38);
            this.ltbGPSDeviceState.Name = "ltbGPSDeviceState";
            this.ltbGPSDeviceState.Size = new System.Drawing.Size(100, 20);
            this.ltbGPSDeviceState.Text = "tbGPSDeviceState";
            // 
            // ltbGPSDevice
            // 
            this.ltbGPSDevice.Location = new System.Drawing.Point(8, 10);
            this.ltbGPSDevice.Name = "ltbGPSDevice";
            this.ltbGPSDevice.Size = new System.Drawing.Size(100, 20);
            this.ltbGPSDevice.Text = "tbGPSDevice";
            // 
            // tbSatellites
            // 
            this.tbSatellites.Location = new System.Drawing.Point(114, 197);
            this.tbSatellites.Name = "tbSatellites";
            this.tbSatellites.Size = new System.Drawing.Size(100, 22);
            this.tbSatellites.TabIndex = 14;
            // 
            // tbLongitude
            // 
            this.tbLongitude.Location = new System.Drawing.Point(114, 169);
            this.tbLongitude.Name = "tbLongitude";
            this.tbLongitude.Size = new System.Drawing.Size(100, 22);
            this.tbLongitude.TabIndex = 13;
            // 
            // tbLatitude
            // 
            this.tbLatitude.Location = new System.Drawing.Point(114, 141);
            this.tbLatitude.Name = "tbLatitude";
            this.tbLatitude.Size = new System.Drawing.Size(100, 22);
            this.tbLatitude.TabIndex = 12;
            // 
            // tbHeading
            // 
            this.tbHeading.Location = new System.Drawing.Point(114, 113);
            this.tbHeading.Name = "tbHeading";
            this.tbHeading.Size = new System.Drawing.Size(100, 22);
            this.tbHeading.TabIndex = 11;
            // 
            // tbGPSServiceState
            // 
            this.tbGPSServiceState.Location = new System.Drawing.Point(114, 64);
            this.tbGPSServiceState.Name = "tbGPSServiceState";
            this.tbGPSServiceState.Size = new System.Drawing.Size(100, 22);
            this.tbGPSServiceState.TabIndex = 10;
            // 
            // tbGPSDeviceState
            // 
            this.tbGPSDeviceState.Location = new System.Drawing.Point(114, 36);
            this.tbGPSDeviceState.Name = "tbGPSDeviceState";
            this.tbGPSDeviceState.Size = new System.Drawing.Size(100, 22);
            this.tbGPSDeviceState.TabIndex = 9;
            // 
            // tbGPSDevice
            // 
            this.tbGPSDevice.Location = new System.Drawing.Point(114, 8);
            this.tbGPSDevice.Name = "tbGPSDevice";
            this.tbGPSDevice.Size = new System.Drawing.Size(100, 22);
            this.tbGPSDevice.TabIndex = 8;
            // 
            // bgpspanelswitch
            // 
            this.bgpspanelswitch.Location = new System.Drawing.Point(183, 9);
            this.bgpspanelswitch.Name = "bgpspanelswitch";
            this.bgpspanelswitch.Size = new System.Drawing.Size(30, 30);
            this.bgpspanelswitch.TabIndex = 9;
            this.bgpspanelswitch.Text = "P";
            this.bgpspanelswitch.Click += new System.EventHandler(this.bgpspanelswitch_Click);
            // 
            // panelSelectMap
            // 
            this.panelSelectMap.Controls.Add(this.bmapsCancel);
            this.panelSelectMap.Location = new System.Drawing.Point(10, 40);
            this.panelSelectMap.Name = "panelSelectMap";
            this.panelSelectMap.Size = new System.Drawing.Size(217, 225);
            this.panelSelectMap.Visible = false;
            // 
            // bmapsCancel
            // 
            this.bmapsCancel.Location = new System.Drawing.Point(142, 198);
            this.bmapsCancel.Name = "bmapsCancel";
            this.bmapsCancel.Size = new System.Drawing.Size(62, 20);
            this.bmapsCancel.TabIndex = 0;
            this.bmapsCancel.Text = "Cancel";
            this.bmapsCancel.Click += new System.EventHandler(this.bmapsCancel_Click);
            // 
            // form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(96F, 96F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Dpi;
            this.AutoScroll = true;
            this.ClientSize = new System.Drawing.Size(240, 268);
            this.Controls.Add(this.panelSelectMap);
            this.Controls.Add(this.pictureBoxGPS);
            this.Controls.Add(this.bgpspanelswitch);
            this.Controls.Add(this.panelGPSDetails);
            this.Controls.Add(this.bgps);
            this.Controls.Add(this.buserzoom);
            this.Controls.Add(this.bminus);
            this.Controls.Add(this.bplus);
            this.Controls.Add(this.pictureBox1);
            this.KeyPreview = true;
            this.Menu = this.mainMenu1;
            this.Name = "form1";
            this.Text = "WM Google Maps";
            this.Deactivate += new System.EventHandler(this.form1_Deactivate);
            this.Load += new System.EventHandler(this.Form1_Load);
            this.Activated += new System.EventHandler(this.form1_Activated);
            this.KeyDown += new System.Windows.Forms.KeyEventHandler(this.form1_KeyDown);
            this.panelGPSDetails.ResumeLayout(false);
            this.panelSelectMap.ResumeLayout(false);
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.MenuItem menuClose;
        private System.Windows.Forms.PictureBox pictureBox1;
        private System.Windows.Forms.Button bplus;
        private System.Windows.Forms.Button bminus;
        private System.Windows.Forms.Button buserzoom;
        private System.Windows.Forms.Button bgps;
        private System.Windows.Forms.MenuItem menuoptions;
        private System.Windows.Forms.PictureBox pictureBoxGPS;
        private System.Windows.Forms.Panel panelGPSDetails;
        private System.Windows.Forms.TextBox tbHeading;
        private System.Windows.Forms.TextBox tbGPSServiceState;
        private System.Windows.Forms.TextBox tbGPSDeviceState;
        private System.Windows.Forms.TextBox tbGPSDevice;
        private System.Windows.Forms.Label ltbSatellites;
        private System.Windows.Forms.Label ltbLongitude;
        private System.Windows.Forms.Label ltbLatitude;
        private System.Windows.Forms.Label ltbHeading;
        private System.Windows.Forms.Label ltbGPSServiceState;
        private System.Windows.Forms.Label ltbGPSDeviceState;
        private System.Windows.Forms.Label ltbGPSDevice;
        private System.Windows.Forms.TextBox tbSatellites;
        private System.Windows.Forms.TextBox tbLongitude;
        private System.Windows.Forms.TextBox tbLatitude;
        private System.Windows.Forms.Button bgpspanelswitch;
        private System.Windows.Forms.MenuItem menugps;
        private System.Windows.Forms.Panel panelSelectMap;
        private System.Windows.Forms.MenuItem menuScreenOrientation;
        private System.Windows.Forms.MenuItem menuSelectMap;
        private System.Windows.Forms.Button bmapsCancel;
        private System.Windows.Forms.MenuItem menuwps;
        private System.Windows.Forms.MenuItem menuShowGPSCoords;

    }
}

