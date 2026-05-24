import React from "react";
import "./middleSide.css";
import ListPost from "../profile/profilePost";
import StoryBlock from "../create/storyBlock";


const MiddleSide: React.FC = () => {

  return (
    <div className="middleHomeSide">
      <div className="storyHome">
        <StoryBlock/>
      </div>

      <ListPost/>
    </div>
  );

};

export default MiddleSide;