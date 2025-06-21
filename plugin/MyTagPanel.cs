using System;
using System.Windows.Forms;

namespace MyTagPlugin
{
    public class MyTagPanel : UserControl
    {
        private TextBox tagInput;
        private ListBox tagList;
        private Button addButton, removeButton;
        private string currentFile;

        public MyTagPanel(string filePath)
        {
            currentFile = filePath;

            tagInput = new TextBox { Top = 10, Left = 10, Width = 150 };
            addButton = new Button { Text = "Add Tag", Top = 10, Left = 170 };
            removeButton = new Button { Text = "Remove Selected", Top = 40, Left = 10 };
            tagList = new ListBox { Top = 70, Left = 10, Width = 250, Height = 120 };

            addButton.Click += AddButton_Click;
            removeButton.Click += RemoveButton_Click;

            Controls.Add(tagInput);
            Controls.Add(addButton);
            Controls.Add(removeButton);
            Controls.Add(tagList);

            LoadTags();
        }

        private void LoadTags()
        {
            tagList.Items.Clear();
            var tags = PythonInterop.GetTagsForFile(currentFile);
            tagList.Items.AddRange(tags);
        }

        private void AddButton_Click(object s, EventArgs e)
        {
            var tag = tagInput.Text.Trim();
            if (!string.IsNullOrEmpty(tag))
            {
                PythonInterop.AddTag(currentFile, tag);
                tagInput.Text = "";
                LoadTags();
            }
        }

        private void RemoveButton_Click(object s, EventArgs e)
        {
            if (tagList.SelectedItem != null)
            {
                var t = tagList.SelectedItem.ToString();
                PythonInterop.RemoveTag(currentFile, t);
                LoadTags();
            }
        }
    }
}
