using System;
using System.Windows.Forms;

namespace MusicBeePlugin
{
    public partial class Plugin
    {
        private PluginInfo about;
        private MusicBeeApiInterface mbApi;

                
        public PluginInfo Initialise(IntPtr apiInterfacePtr)
        {
            about = new PluginInfo
            {
                PluginInfoVersion = 1,
                Name = "Rekordbox MyTag Viewer",
                Description = "Shows My Tags from Rekordbox for matching files",
                Author = "You & ChatGPT 😎",
                VersionMajor = 1,
                VersionMinor = 0
            };
            PythonInterop.InitializePython();

            return about;
        }

        public bool Configure(IntPtr panelHandle)
        {
          string filePath = mbApi.NowPlaying_GetFileUrl();
          Form tagEditorForm = new Form()
           {
              Text = "Edit Rekordbox My Tags",
             Width = 300,
                Height = 250
            };

            var panel = new MyTagPanel(filePath);
            tagEditorForm.Controls.Add(panel);
            tagEditorForm.ShowDialog();

            return false;
        }

        public void Close(PluginCloseReason reason) => PythonInterop.ShutdownPython();
        public void ReceiveNotification(string sourceFileUrl, NotificationType type) { }
    }
}
