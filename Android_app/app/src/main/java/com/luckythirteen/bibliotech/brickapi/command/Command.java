package com.luckythirteen.bibliotech.brickapi.command;

import com.google.gson.Gson;

public abstract class Command {
    transient CommandType commandType = CommandType.undefined;

    public String toJSONString() {
        Gson gson = new Gson();

        return "{\"" + this.commandType.name() + "\":" + (gson.toJson(this)) + "}";
    }

}
