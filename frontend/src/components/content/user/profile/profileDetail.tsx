import './profileDetail.css';
import WorkIcon from '@mui/icons-material/Work';
import PlaceIcon from '@mui/icons-material/Place';
import GroupIcon from '@mui/icons-material/Group';
import AccessTimeIcon from '@mui/icons-material/AccessTime';


const ProfileDetail = () => {
    return (
        <div className="profileDetail">
            <div className="imageDIv-detail">
                <div className="avatar-wrapper">
                    <img
                        className="faculty-avatar"
                        src="https://fit.hcmute.edu.vn/Resources/Images/SubDomain/fit/logo-cntt2021.png"
                        alt="faculty-avatar"
                    />
                </div>
            </div>
            <div className="profile-info-detail">
                <div className="detail-description">
                    <div className="detail-description-icon">
                        <WorkIcon />
                    </div>
                    <span className="detail-description-text">Đã tốt nghiệp HCMUTE ngành Công Nghệ thông Tin</span>
                </div>
                <div className="detail-description">
                    <div className="detail-description-icon">
                        <PlaceIcon />
                    </div>
                    <span className="detail-description-text">Sống tại thành phố Hồ Chí Minh</span>
                </div>
                <div className="detail-description">
                    <div className="detail-description-icon">
                        <GroupIcon />
                    </div>
                    <span className="detail-description-text">Là thành viên khoa Công Nghệ thông Tin</span>
                </div>
                <div className="detail-description">
                    <div className="detail-description-icon">
                        <AccessTimeIcon />
                    </div>
                    <span className="detail-description-text">Tuổi UTEzone: 2 năm</span>
                </div>
            </div>
        </div>
    );
}

export default ProfileDetail;