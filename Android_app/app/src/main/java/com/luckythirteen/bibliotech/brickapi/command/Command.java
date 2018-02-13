package com.luckythirteen.bibliotech.brickapi.command;

import com.google.gson.Gson;

public abstract class Command {
    protected transient CommandType commandType = CommandType.undefined;

    public String toJSONString() {
        Gson gson = new Gson();
        String jsonString = "{\"" + this.commandType.name() + "\":" + (gson.toJson(this)) + "}";

        return jsonString;
    }

}
