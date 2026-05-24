import React, { useState } from "react";
import "./searchUser.css";
import { jwtDecode } from "jwt-decode";
import { FollowButton } from "../relationship/follow";
import { UnFollowButton } from "../relationship/unfollow";
import { useNavigate } from "react-router-dom";

interface Props {
  users: any[];
}

interface JwtPayload {
  sub: string;
  exp: number;
}

const SearchUser = ({ users }: Props) => {
  const [userList, setUserList] = useState(users);

  // Lấy email người dùng hiện tại từ token
  const token = localStorage.getItem("token");
  let currentUserEmail: string | null = null;
  if (token) {
    try {
      const decoded: JwtPayload = jwtDecode<JwtPayload>(token);
      currentUserEmail = decoded.sub;
    } catch (err) {
      console.error("❌ Token không hợp lệ:", err);
    }
  }
  const navigate = useNavigate();

  const goToProfile = (email: string) => {
    navigate(`/profile/${email}`);
  };

  return (
    <div className="tab-content">
      {userList.length === 0 ? (
        <p>Không tìm thấy người dùng</p>
      ) : (
        userList.map((user) => {
          const hasFollowed = user.userInfo?.followers?.includes(
            currentUserEmail || ""
          );

          return (
            <div key={user._id} className="user-card">
              <div className="user-info">
                <img
                  src={
                    user.userInfo?.avatar || "https://via.placeholder.com/50"
                  }
                  className="user-avatar"
                  alt="avatar"
                  style={{ cursor: "pointer" }}
                  onClick={() => goToProfile(user.email)}
                />
                <div
                  className="user-text"
                  style={{ cursor: "pointer" }}
                  onClick={() => goToProfile(user.email)}
                >
                  <h4>{user.userInfo?.fullName || user.email}</h4>
                </div>
              </div>

              {hasFollowed ? (
                <UnFollowButton
                  ownerEmail={currentUserEmail || ""}
                  clientEmail={user.email}
                  onUnFollowSuccess={() => {
                    setUserList((prev) =>
                      prev.map((u) =>
                        u._id === user._id
                          ? {
                              ...u,
                              userInfo: {
                                ...u.userInfo,
                                followers: (u.userInfo?.followers || []).filter(
                                  (f: string | null) => f !== currentUserEmail
                                ),
                              },
                            }
                          : u
                      )
                    );
                  }}
                />
              ) : (
                <FollowButton
                  ownerEmail={currentUserEmail || ""}
                  clientEmail={user.email}
                  onFollowSuccess={() => {
                    setUserList((prev) =>
                      prev.map((u) =>
                        u._id === user._id
                          ? {
                              ...u,
                              userInfo: {
                                ...u.userInfo,
                                followers: [
                                  ...(u.userInfo?.followers || []),
                                  currentUserEmail || "",
                                ],
                              },
                            }
                          : u
                      )
                    );
                  }}
                />
              )}
            </div>
          );
        })
      )}
    </div>
  );
};

export default SearchUser;
