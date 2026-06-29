# 5-Minute Video Presentation Transcript

## Slide 1 - Title

Hello, my name is Matthias Mifsud, and this presentation covers my project, **Benchmarking Small-Object Detection on Brain MRI: A Cerebral Microbleed Case Study**. The project focuses on automated cerebral microbleed detection using brain MRI data, and on how these detections can be evaluated more transparently. I will introduce the problem, describe the nnU-Net pipeline, and present the dashboard developed to inspect the results.

## Slide 2 - Problem

Cerebral microbleeds are tiny deposits of blood in the brain. They are usually visible on specialised MRI sequences, especially T2-star weighted images, where they appear as small dark spots. Clinically, they are important because they are associated with stroke, cognitive decline, and cerebral small-vessel disease.

Manual detection is difficult. A radiologist may need to inspect hundreds of MRI slices for one subject, and the lesions can resemble blood vessels or other anatomical structures. This makes review slow, error-prone, and sometimes inconsistent between observers. The motivation for this project is therefore to automate part of the process using deep learning, while keeping the results interpretable.

## Slide 3 - Current Limitations

Even when an automated model performs well, there is still an important question: how do we know whether we can trust the output?

Standard metrics such as sensitivity, F1-score, and Dice coefficient are useful, but for tiny objects they do not always tell the full story. Dice is based on voxel-level overlap, so a small localisation error can cause a large drop, even when the prediction is close to the correct location.

A summary score also does not explain where the model failed, which subjects were difficult, or whether a missed lesion was actually detected with lower confidence. So the problem is not only detection accuracy. It is also evaluation transparency.

## Slide 4 - Automated Detection and Visual Evaluation Pipeline

To address this, the project implements a full automated pipeline. First, the VALDO dataset is prepared and converted into the required nnU-Net structure. This includes organising the MRI volumes and labels, checking that the masks are valid, and confirming that image and label dimensions are aligned.

Next, nnU-Net is trained as the baseline model. It automatically configures many parts of the segmentation process based on the dataset properties. In this project, a 2D full-resolution configuration was used because of the computational constraints of training on MRI volumes.

After training, the model generates prediction masks and probability maps for each subject. These outputs are evaluated using connected-component analysis, where predicted microbleed candidates are matched against the ground truth. Finally, the outputs are loaded into an interactive dashboard for visual inspection.

## Slide 5 - Dashboard

The dashboard is the individual research contribution of the project. It was built using Streamlit and is designed to make evaluation more interpretable.

Users can inspect the MRI volume slice by slice across axial, sagittal, and coronal views, while seeing the predictions directly over the scan. The overlays are colour-coded: correct detections are shown in green, false positives in red, and missed lesions in yellow.

The dashboard also supports interactive thresholding. Since nnU-Net outputs probability maps, the user can adjust the threshold in real time. This shows whether a missed lesion was completely ignored, or whether it was detected with lower confidence and excluded by the default threshold.

Finally, the dashboard includes summary tables and graphs, helping identify subjects where the model underperformed so they can be inspected in more detail.

## Slide 6 - Findings

The results show that the model performs strongly overall. Across all evaluated subjects, the mean sensitivity was 96 percent, the mean F1-score was 97 percent, and the mean Dice coefficient was 90 percent. The median sensitivity and median F1-score were both 100 percent, meaning that for most subjects the model achieved perfect lesion-level detection.

No false-positive detections were recorded in the reported evaluation, which indicates very high precision. At the same time, the dashboard showed that some apparent false negatives were not complete failures. In several cases, lowering the probability threshold converted missed lesions into true positives. This suggests that some errors were linked to probability calibration rather than the model failing to localise the lesion.

The model struggled most with edge cases, especially subjects with very high microbleed counts or very small clustered lesions. These are exactly the cases where visual inspection is valuable.

## Slide 7 - Conclusion

To conclude, this project demonstrates that automated detection can reduce the workload involved in reviewing MRI scans for cerebral microbleeds. The nnU-Net baseline achieved strong performance, particularly at the lesion level.

However, the project also shows that standard metrics are not enough on their own. For small-object detection, lesion-level metrics are often more informative than voxel-level metrics, and visual inspection is essential for understanding model behaviour.

The dashboard helps explain where and why the model succeeds or fails. It gives researchers a way to inspect detections, adjust thresholds, compare subjects, and connect numerical results back to the original MRI data.

Although this project focuses on cerebral microbleeds, the same approach could be adapted to other small-object detection problems in medical imaging, where transparency and trust are just as important as raw performance.

Thank you for watching.
