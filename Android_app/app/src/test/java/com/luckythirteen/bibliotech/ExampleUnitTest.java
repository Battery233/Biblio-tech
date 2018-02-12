package com.luckythirteen.bibliotech;

import com.luckythirteen.bibliotech.brickapi.obj.InputPort;

import org.junit.Assert;
import org.junit.Test;

import static org.junit.Assert.*;

/**
 * Example local unit test, which will execute on the development machine (host).
 *
 * @see <a href="http://d.android.com/tools/testing">Testing documentation</a>
 */
public class ExampleUnitTest
{
    @Test
    public void addition_isCorrect() throws Exception
    {
        Assert.assertEquals(InputPort.FOUR.toString(), "in4");
    }
}