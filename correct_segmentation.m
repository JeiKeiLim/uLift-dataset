function [outputArg1,outputArg2] = correct_segmentation(segment_csv_name)

ROOT = '/Users/jeikei/Dropbox/Workspaces/liftingRecognitionWorkspace/2018_ActmoFitDataCollector_Dataset/sensor/';

% segment_csv_name = 'An_2019_0117_191037_segment02_02';
split_csv_name = strsplit(segment_csv_name, '_');
whole_name = strcat([split_csv_name{1}, '_', split_csv_name{2}, '_', split_csv_name{3}, '_', split_csv_name{4}, '_whole']);

n_rest_session = str2double(strrep(split_csv_name{5}, 'segment', '')) + 1;
rest_name = strcat([split_csv_name{1}, '_', split_csv_name{2}, '_', split_csv_name{3}, '_', split_csv_name{4}, '_', sprintf('segment%02d_rest', n_rest_session) ]);

csv_path = strcat([ROOT, split_csv_name{1}, '/', segment_csv_name, '.csv']);
rest_path = strcat([ROOT, split_csv_name{1}, '/', rest_name, '.csv']);
whole_path = strcat([ROOT, split_csv_name{1}, '/', whole_name, '.csv']);

csv_data = csvread(csv_path);
whole_data = csvread(whole_path);
rest_data = csvread(rest_path);

whole_csv_index = find(whole_data(:,2) == csv_data(length(csv_data),2));
whole_csv_index = whole_csv_index(length(whole_csv_index));

segment_info_index = find(whole_data(whole_csv_index:whole_csv_index+20, 1) == -2);
segment_info_index = whole_csv_index + segment_info_index - 1;
segment_data = whole_data(segment_info_index, :);

whole_data(segment_info_index,:) = [];

EXAMINE_LENGTH = 1001;

examine_data = [csv_data(:,3:5); whole_data(whole_csv_index+1:whole_csv_index+EXAMINE_LENGTH,3:5)];
hold off;
subplot(2,3, 1:3);
plot(examine_data);
hold on;
plot([length(csv_data) length(csv_data)], [min(examine_data(:)) max(examine_data(:))], 'k-')
[x,y] = ginput(1);
x = floor(x);

add_up_index = (whole_csv_index+1):whole_csv_index+(x-length(csv_data))+1;
plot([x x], [min(examine_data(:)) max(examine_data(:))], 'k-')

subplot(2,3, 4:5);
plot([csv_data(:,3:5); whole_data(add_up_index, 3:5)]);

segment_data(2) = whole_data(add_up_index(length(add_up_index)),2);
whole_data = [whole_data(1:add_up_index(length(add_up_index)),:); segment_data; whole_data(add_up_index(length(add_up_index))+1:length(whole_data),:)];
csv_data = [csv_data; whole_data(add_up_index, :)];

rest_cut_index = find(rest_data(:,2) == whole_data(add_up_index(length(add_up_index)),2));
rest_cut_index = rest_cut_index(length(rest_cut_index));
rest_data = rest_data(rest_cut_index+1:length(rest_data), :);

subplot(2,3, 6);
plot(rest_data(:,3:5));

dlmwrite(csv_path, csv_data, 'precision', 13);
dlmwrite(rest_path, rest_data, 'precision', 13);
dlmwrite(whole_path, whole_data, 'precision', 13);


end

