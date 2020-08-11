function play_sensor_and_video(video_root, video_name)
    global KEY_IS_PRESSED
    KEY_IS_PRESSED = 0;
% Example call
% play_sensor_and_video('../video/', 'Jongkuk/Jongkuk_2019_0106_200857_whole');
%
%     PLAY_NAME = 'Jongkuk/Jongkuk_2019_0106_200857_whole';
%     VIDEO_ROOT = '../video/';

    close all;
    
    PLAY_NAME = video_name;
    VIDEO_ROOT = video_root;

    SENSOR_PATH = strcat(['./', PLAY_NAME, '.csv']);
    VIDEO_PATH = strcat([VIDEO_ROOT, PLAY_NAME, '.MOV']);

    data = csvread(SENSOR_PATH);
    video = VideoReader(VIDEO_PATH);

    t = data(:,2) / 1000;
    sensor = data(:,3:5);

    total_time = (t(length(t)) - t(1));

    % Fixing timestamp due to the delayed arrival of BLE
    t = t - t(1);

    W_SIZE = 60 * 8;
    min_v = min(sensor(:));

    sensor_inv = abs(-sensor - min_v) * 3;

    fig = figure('Renderer', 'painters', 'Position', [1 1 560 954]);
    set(fig, 'KeyPressFcn', @myKeyPressFcn) 
    
    hold off;
    ax_img = image(video.readFrame);
    set(gcf,'MenuBar','none')
    set(gca,'DataAspectRatioMode','auto');
    set(gca,'Position',[0 0 1 1]);
    hold on;
    ax_sensor = plot(linspace(0, video.Width, W_SIZE), sensor_inv(1:W_SIZE,:), 'LineWidth', 3);
    axis('off')

    max_video_idx_in_t = find(t > video.Duration, 1) - 1;
    sensor_x = linspace(1, video.Width+1, W_SIZE);

    v_writer = VideoWriter(strcat([VIDEO_ROOT, PLAY_NAME, '_sensor.mp4']), 'MPEG-4');
    v_writer.FrameRate = video.FrameRate;

    open(v_writer);
    
    for i=(W_SIZE+1):max_video_idx_in_t
        video.currentTime = t(i);
        
        try
            ax_img.CData = video.readFrame;
        catch
            disp('end of the video!');
            break;
        end

        ax_sensor(1).YData = sensor_inv((i-W_SIZE):(i-1),1);
        ax_sensor(2).YData = sensor_inv((i-W_SIZE):(i-1),2);
        ax_sensor(3).YData = sensor_inv((i-W_SIZE):(i-1),3);

        v_writer.writeVideo(getframe(gcf));
        
        if KEY_IS_PRESSED == 1
            break;
        end
    end

    close(v_writer);
    
    
    function myKeyPressFcn(hObject, event)
        key = get(gcf,'CurrentCharacter');
        if key == 'q'
            KEY_IS_PRESSED  = 1;
        end
    end
end
