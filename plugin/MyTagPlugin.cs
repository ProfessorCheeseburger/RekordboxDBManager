using System;
using MusicBeePlugin; 
using System.Windows.Forms;

namespace MyTagPlugin
{
    public class Plugin : MusicBeePluginInterface
    {
        private PluginInfo about = new PluginInfo();
        private MusicBeeApiInterface mbApi;

        public PluginInfo Initialise(IntPtr apiInterfacePtr)
        {
            mbApi = new MusicBeeApiInterface();
            mbApi.Initialise(apiInterfacePtr);

            about.PluginInfoVersion = PluginInfoVersion;
            about.Name = "Rekordbox MyTag Viewer";
            about.Description = "Shows My Tags from Rekordbox for matching files";
            about.Author = "You & ChatGPT 😎";
            about.VersionMajor = 1;
            about.VersionMinor = 0;

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
