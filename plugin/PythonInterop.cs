using System;
using System.IO;
using Python.Runtime;

namespace MyTagPlugin
{
    public static class PythonInterop
    {
		private static bool initialized = false;
		public static void InitializePython()
		{
			if (initialized) return;

			var pythonHome = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "python");
			Environment.SetEnvironmentVariable("PYTHONHOME", pythonHome);
			Environment.SetEnvironmentVariable("PYTHONPATH", pythonHome + ";"
				+ Path.Combine(pythonHome, "Lib") + ";"
				+ Path.Combine(pythonHome, "site-packages"));

			Runtime.PythonDLL = "python310.dll";
			PythonEngine.Initialize();
			initialized = true;
		}

        public static string[] GetTagsForFile(string filePath)
        {
            using (Py.GIL())
            {
                dynamic bridge = Py.Import("mytag_bridge");
                dynamic tags = bridge.get_tags_for_file(filePath);
                return tags.ToString().Trim('[', ']').Split(new[] { ',' }, StringSplitOptions.RemoveEmptyEntries);
            }
        }

        public static void ShutdownPython()
        {
            PythonEngine.Shutdown();
        }
		
		public static bool AddTag(string filePath, string tag)
		{
			using (Py.GIL())
			{
				dynamic bridge = Py.Import("mytag_bridge");
				return bridge.add_tag_to_file(filePath, tag);
			}
		}

		public static bool RemoveTag(string filePath, string tag)
		{
			using (Py.GIL())
			{
				dynamic bridge = Py.Import("mytag_bridge");
				return bridge.remove_tag_from_file(filePath, tag);
			}
		}

		public static bool SetTags(string filePath, string[] tags)
		{
			using (Py.GIL())
			{
				dynamic bridge = Py.Import("mytag_bridge");
				dynamic pyList = new PyList();
				foreach (var tag in tags)
					pyList.Append(new PyString(tag.Trim()));

				return bridge.set_tags_for_file(filePath, pyList);
			}
		}

    }
}
